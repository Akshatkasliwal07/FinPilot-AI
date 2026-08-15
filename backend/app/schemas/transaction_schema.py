from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class TransactionCreate(BaseModel):
    amount: float
    type: str
    category: str
    description: Optional[str] = None
    date: date


class TransactionResponse(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    description: Optional[str]
    date: date
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True