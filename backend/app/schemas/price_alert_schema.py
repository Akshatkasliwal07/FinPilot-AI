from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


class PriceAlertCreate(BaseModel):

    stock_symbol: str

    target_price: float = Field(
        gt=0,
        description="Target price must be greater than 0"
    )

    condition: str = Field(
        description="above or below"
    )


class PriceAlertResponse(BaseModel):

    id: int

    stock_symbol: str

    target_price: float

    condition: str

    is_triggered: bool

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )