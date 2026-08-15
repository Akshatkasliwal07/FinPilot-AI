from ai.config.llm import llm
from ai.tools.fundamental_tool import get_fundamental_data
from ai.prompts.fundamental_prompt import FUNDAMENTAL_PROMPT


def fundamental_agent(symbol: str):

    data = get_fundamental_data(symbol)

    if "error" in data:
        return {
            "success": False,
            "message": data["error"],
            "data": {}
        }

    prompt = FUNDAMENTAL_PROMPT.format(
        financial_data=data
    )

    response = llm.invoke(prompt)

    summary = response.content

    if isinstance(summary, list):
        summary = "".join(
            block.get("text", "")
            for block in summary
            if isinstance(block, dict)
        )

    return {
        "success": True,
        "message": "Fundamental analysis completed.",
        "data": {
            "financials": data,
            "analysis": summary
        }
    }