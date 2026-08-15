import os
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"

load_dotenv(ENV_FILE)

# Provider selection
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

# Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.0-flash",
)

# Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile",
)

# Shared LLM settings
LLM_TEMPERATURE = float(
    os.getenv("LLM_TEMPERATURE", "0.2")
)

LLM_MAX_RETRIES = int(
    os.getenv("LLM_MAX_RETRIES", "2")
)

# Other AI services
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2",
)

CHROMA_PERSIST_DIRECTORY = BACKEND_DIR / os.getenv(
    "CHROMA_PERSIST_DIRECTORY",
    "data/chroma",
)

CHROMA_COLLECTION = os.getenv(
    "CHROMA_COLLECTION",
    "finpilot_documents",
)


def validate_llm_config() -> None:
    if LLM_PROVIDER == "groq" and not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is missing from backend/.env."
        )

    if LLM_PROVIDER == "gemini" and not GOOGLE_API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY is missing from backend/.env."
        )

    if LLM_PROVIDER not in {"groq", "gemini"}:
        raise RuntimeError(
            "LLM_PROVIDER must be either 'groq' or 'gemini'."
        )