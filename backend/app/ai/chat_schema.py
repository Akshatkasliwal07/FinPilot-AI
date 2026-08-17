from pydantic import BaseModel, Field
from typing import Literal


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)

    history: list[ChatMessage] = Field(
        default_factory=list
    )


class AIChatResponse(BaseModel):
    reply: str

    market_context: dict | None = None

    timestamp: str
