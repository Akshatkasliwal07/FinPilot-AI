from langchain_core.messages import HumanMessage

from ai.models.llm import llm
from ai.models.response import error_response, success_response


def report_agent(state: dict) -> dict:
    prompt = f"""
You are a Senior Equity Research Analyst.

Create a structured financial research report using only the data below.

Company:
{state.get("company", "Not available")}

Market Data:
{state.get("market_data", {})}

News:
{state.get("news_data", {})}

Company Research:
{state.get("company_data", {})}

Fundamental Analysis:
{state.get("fundamental_analysis", {})}

Technical Analysis:
{state.get("technical_analysis", {})}

Portfolio Analysis:
{state.get("portfolio_analysis", {})}

Risk Analysis:
{state.get("risk_analysis", {})}

Use these sections:

# Executive Summary
# Company Overview
# Market Performance
# Latest News
# Fundamental Analysis
# Technical Analysis
# Portfolio Considerations
# Risk Analysis
# Conclusion

Rules:
- Do not invent facts.
- Mention unavailable data clearly.
- Do not guarantee returns.
- Keep conclusions balanced and evidence-based.
"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])

        return success_response(
            "Final report generated.",
            response.content,
        )

    except Exception as error:
        return error_response(str(error))