from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict
)


class StockBase(BaseModel):
    symbol: str
    company_name: str
    exchange: str
    sector: Optional[str] = None
    industry: Optional[str] = None


class StockCreate(StockBase):
    pass


class StockResponse(StockBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )