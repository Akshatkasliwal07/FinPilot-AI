from typing import Generic, Optional, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None


class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int
    total_pages: int


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    path: str


class MessageResponse(BaseModel):
    success: bool = True
    message: str