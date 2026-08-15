from ai.config.llm import llm
from ai.tools.technical_tool import get_technical_data
from ai.prompts.technical_prompt import TECHNICAL_PROMPT


def technical_agent(symbol: str):

    technical_data = get_technical_data(symbol)

    if "error" in technical_data:
        return {
            "success": False,
            "message": technical_data["error"],
            "data": {}
        }

    prompt = TECHNICAL_PROMPT.format(
        technical_data=technical_data
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
        "message": "Technical analysis completed.",
        "data": {
            "technical_data": technical_data,
            "analysis": summary
        }
    }