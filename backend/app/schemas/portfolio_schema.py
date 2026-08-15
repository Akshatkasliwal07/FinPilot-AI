from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict
)


# ---------------------------------
# Create Portfolio
# ---------------------------------

class PortfolioCreate(BaseModel):
    stock_symbol: str
    quantity: int
    purchase_price: float


# ---------------------------------
# Portfolio Response
# ---------------------------------

class PortfolioResponse(BaseModel):
    id: int
    stock_symbol: str
    quantity: int
    purchase_price: float
    purchase_date: datetime
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ---------------------------------
# Portfolio Summary Item
# ---------------------------------

class PortfolioSummaryItem(BaseModel):
    id: int
    stock_symbol: str
    quantity: int
    purchase_price: float
    live_price: float
    invested_amount: float
    current_value: float
    profit_loss: float
    return_percentage: float


# ---------------------------------
# Portfolio Summary Response
# ---------------------------------

class PortfolioSummaryResponse(BaseModel):
    total_invested: float
    current_value: float
    profit_loss: float
    return_percentage: float
    holdings: int
    items: list[PortfolioSummaryItem]