from typing import Any

from pydantic import BaseModel, Field


class AIServiceResponse(BaseModel):
    success: bool
    message: str
    data: dict[str, Any]


class AIChatRequest(BaseModel):
    session_id: str = Field(
        min_length=1,
        max_length=200
    )

    user_query: str = Field(
        min_length=1,
        max_length=5000
    )


class AIResearchRequest(BaseModel):
    user_query: str = Field(
        min_length=1,
        max_length=5000
    )


class PDFQuestionRequest(BaseModel):
    source: str = Field(
        min_length=1,
        max_length=255
    )

    question: str = Field(
        min_length=1,
        max_length=5000
    )