from langchain_core.messages import HumanMessage

from ai.models.llm import llm
from ai.models.response import error_response, success_response


def risk_agent(state: dict) -> dict:
    market_data = state.get("market_data", {})
    fundamental_data = state.get("fundamental_analysis", {})
    technical_data = state.get("technical_analysis", {})

    prompt = f"""
You are a Senior Equity Risk Analyst.

Analyze the investment risks only from the supplied information.

Market Data:
{market_data}

Fundamental Analysis:
{fundamental_data}

Technical Analysis:
{technical_data}

Provide:

1. Business risks
2. Financial risks
3. Technical risks
4. Macroeconomic risks
5. Risk level: Low, Medium, or High
6. Risk score: 0 to 100
7. Investment suitability
8. A balanced final recommendation

Rules:
- Do not invent facts.
- State when data is missing.
- Do not guarantee investment outcomes.
"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])

        return success_response(
            "Risk analysis completed.",
            response.content,
        )

    except Exception as error:
        return error_response(str(error))