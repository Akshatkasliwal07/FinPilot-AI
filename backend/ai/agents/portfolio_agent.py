from ai.config.llm import llm
from ai.models.response import error_response, success_response


def portfolio_agent(state: dict) -> dict:
    user_query = state.get("user_query", "")
    portfolio = state.get("portfolio", [])

    prompt = f"""
You are a professional portfolio analyst.

Portfolio Holdings:
{portfolio}

Investor Request:
{user_query}

Provide:
1. Portfolio allocation analysis
2. Risk assessment
3. Diversification suggestions
4. Long-term improvement ideas

Rules:
- Use only the supplied portfolio holdings and request.
- Do not mention companies that are absent from Portfolio Holdings.
- State clearly when data is missing.
- Do not promise returns.
- Do not give personalized financial advice.
"""

    try:
        response = llm.invoke(prompt)

        return success_response(
            "Portfolio analysis completed.",
            response.content,
        )

    except Exception as error:
        return error_response(str(error))