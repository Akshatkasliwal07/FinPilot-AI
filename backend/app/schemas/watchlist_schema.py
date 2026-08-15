from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WatchlistCreate(BaseModel):
    stock_symbol: str


class WatchlistResponse(BaseModel):
    id: int
    stock_symbol: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )