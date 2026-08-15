from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from ai.config.settings import (
    GEMINI_MODEL,
    GOOGLE_API_KEY,
    GROQ_MODEL,
    LLM_MAX_RETRIES,
    LLM_PROVIDER,
    LLM_TEMPERATURE,
    validate_llm_config,
)


@lru_cache(maxsize=1)
def get_llm():
    """
    Return the configured FinPilot LLM client.
    """
    validate_llm_config()

    if LLM_PROVIDER == "groq":
        return ChatGroq(
            model=GROQ_MODEL,
            temperature=LLM_TEMPERATURE,
            max_retries=LLM_MAX_RETRIES,
        )

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=LLM_TEMPERATURE,
        max_retries=LLM_MAX_RETRIES,
    )


class LazyLLM:
    def invoke(self, *args, **kwargs):
        return get_llm().invoke(*args, **kwargs)


llm = LazyLLM()