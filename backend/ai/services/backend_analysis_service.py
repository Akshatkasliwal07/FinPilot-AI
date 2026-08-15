import json
from typing import Any

from ai.config.llm import llm
from ai.models.response import error_response, success_response

from app.services.technical_analysis_service import (
    TechnicalAnalysisService,
)

VALID_RECOMMENDATIONS = {"BUY", "HOLD", "SELL"}


def _extract_text(content: Any) -> str:
    """Convert a LangChain/Groq response content value to text."""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict)
        )

    return str(content)


def _extract_json(text: str) -> dict:
    """
    Extract JSON even if the LLM wraps it
    in a Markdown code block.
    """

    cleaned_text = text.strip()

    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.replace(
            "```json",
            "",
            1,
        )

        cleaned_text = cleaned_text.replace(
            "```",
            "",
            1,
        ).strip()

    start = cleaned_text.find("{")
    end = cleaned_text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            "AI response did not contain valid JSON."
        )

    return json.loads(
        cleaned_text[start:end + 1]
    )


def _validate_analysis(data: dict) -> dict:
    """
    Validate the strict response expected
    by the FastAPI backend.
    """

    recommendation = str(
        data.get("recommendation", "")
    ).upper().strip()

    if recommendation not in VALID_RECOMMENDATIONS:
        raise ValueError(
            "Recommendation must be BUY, HOLD, or SELL."
        )

    try:
        confidence = int(
            data.get("confidence")
        )

    except (TypeError, ValueError) as error:
        raise ValueError(
            "Confidence must be an integer from 0 to 100."
        ) from error

    if confidence < 0 or confidence > 100:
        raise ValueError(
            "Confidence must be between 0 and 100."
        )

    reason = str(
        data.get("reason", "")
    ).strip()

    if not reason:
        raise ValueError(
            "Reason must not be empty."
        )

    return {
        "recommendation": recommendation,
        "confidence": confidence,
        "reason": reason,
    }


def run_backend_analysis(
    symbol: str,
    current_price: float | int | None,
    technical_indicators: dict | None,
    latest_news: list[dict] | None,
) -> dict:
    """
    FinPilot AI backend analysis.

    The FastAPI backend supplies the stock data.
    Technical indicators are calculated from the
    supplied historical data when available.
    """

    # -------------------------------------------------
    # Validate symbol
    # -------------------------------------------------

    if not symbol or not symbol.strip():
        return error_response(
            "symbol is required."
        )

    # -------------------------------------------------
    # Normalize input
    # -------------------------------------------------

    supplied_indicators = (
        technical_indicators or {}
    )

    news = latest_news or []

    # -------------------------------------------------
    # Extract historical data
    # -------------------------------------------------

    history = supplied_indicators.get(
        "historical_data",
        [],
    )

    # -------------------------------------------------
    # Calculate technical indicators
    # -------------------------------------------------

    calculated_indicators = {}

    if history:

        technical_result = (
            TechnicalAnalysisService
            .calculate_indicators(history)
        )

        if technical_result["success"]:
            calculated_indicators = (
                technical_result["data"]
            )

        else:
            calculated_indicators = {}

    # -------------------------------------------------
    # Remove raw historical data from the
    # indicator section sent to the LLM.
    #
    # We don't need to send every OHLC row because
    # the calculated indicators summarize the data.
    # -------------------------------------------------

    cleaned_indicators = {
        key: value
        for key, value in supplied_indicators.items()
        if key != "historical_data"
    }

    # -------------------------------------------------
    # Merge supplied + calculated indicators
    # -------------------------------------------------

    final_indicators = {
        **cleaned_indicators,
        **calculated_indicators,
    }

    # -------------------------------------------------
    # Build AI payload
    # -------------------------------------------------

    payload = {
        "symbol": symbol.strip().upper(),
        "current_price": current_price,
        "technical_indicators": final_indicators,
        "latest_news": news,
    }

    # -------------------------------------------------
    # AI Prompt
    # -------------------------------------------------

    prompt = f"""
You are FinPilot AI, a careful financial-analysis assistant.

Analyze only the supplied market data below.

Do not use outside knowledge.
Do not invent missing metrics, news, prices, or company facts.
Do not guarantee returns.
Do not provide personalized financial advice.

Supplied market data:

{json.dumps(
    payload,
    ensure_ascii=False,
    default=str,
    indent=2,
)}

Your task is to evaluate the supplied technical
and market information and produce one of:

BUY
HOLD
SELL

Return valid JSON only.

Do not use Markdown.
Do not use code fences.

Required JSON format:

{{
    "recommendation": "BUY, HOLD, or SELL",
    "confidence": 0,
    "reason": "A concise evidence-based explanation using only supplied data."
}}

Rules:

- recommendation must be exactly BUY, HOLD, or SELL.
- confidence must be an integer from 0 to 100.
- reason must be concise and evidence-based.
- Use the technical indicators when they are available.
- Consider trend, SMA, RSI, MACD, volume,
  volatility, support, and resistance.
- Do not invent values when an indicator is missing.
- If the supplied data is limited or contradictory,
  prefer HOLD and lower confidence.
- RSI above 70 may indicate overbought conditions.
- RSI below 30 may indicate oversold conditions.
- A bullish MACD direction can support positive momentum.
- A bearish MACD direction can support negative momentum.
- Price above SMA can support a bullish trend.
- Price below SMA can support a bearish trend.
- Support and resistance should be treated as
  reference levels, not guaranteed price targets.
"""

    # -------------------------------------------------
    # Call LLM
    # -------------------------------------------------

    try:

        response = llm.invoke(prompt)

        response_text = _extract_text(
            response.content
        )

        analysis = _extract_json(
            response_text
        )

        validated_analysis = (
            _validate_analysis(
                analysis
            )
        )

        return success_response(
            "AI analysis completed successfully.",
            validated_analysis,
        )

    except Exception as error:

        return error_response(
            f"AI analysis could not be completed: {error}"
        )