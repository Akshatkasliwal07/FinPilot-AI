from pydantic import BaseModel


class DashboardUser(BaseModel):
    id: int
    name: str
    email: str


class DashboardPortfolio(BaseModel):
    total_invested: float
    current_value: float
    profit_loss: float
    return_percentage: float
    holdings: int


class DashboardWatchlistItem(BaseModel):
    id: int
    stock_symbol: str


class DashboardPriceAlertItem(BaseModel):
    id: int
    stock_symbol: str
    target_price: float
    condition: str
    is_triggered: bool


class DashboardData(BaseModel):
    user: DashboardUser
    portfolio: DashboardPortfolio
    watchlist: list[DashboardWatchlistItem]
    price_alerts: list[DashboardPriceAlertItem]
    watchlist_count: int
    alerts_count: int