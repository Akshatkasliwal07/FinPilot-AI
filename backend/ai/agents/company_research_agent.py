from ai.tools.company_tool import get_company_profile
from ai.prompts.company_prompt import COMPANY_RESEARCH_PROMPT
from ai.config.gemini import llm


def company_research_agent(symbol: str):

    company = get_company_profile(symbol)

    if "error" in company:
        return {
            "success": False,
            "message": company["error"],
            "data": {}
        }

    prompt = COMPANY_RESEARCH_PROMPT.format(
        company_data=company
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
        "message": "Company profile generated successfully.",
        "data": {
            "company": company,
            "summary": summary
        }
    }