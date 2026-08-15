from pathlib import Path
from ai.config.gemini import llm

# Load system prompt
prompt_path = Path(__file__).parent.parent / "prompts" / "planner_prompt.txt"

with open(prompt_path, "r", encoding="utf-8") as file:
    SYSTEM_PROMPT = file.read()


def planner_agent(user_query: str):
    prompt = f"""
{SYSTEM_PROMPT}

User Request:
{user_query}
"""

    response = llm.invoke(prompt)

    if isinstance(response.content, list):
        return response.content[0]["text"]

    return response.content