from sqlalchemy.orm import Session

from app.repositories.watchlist_repository import (
    WatchlistRepository
)
from app.repositories.price_alert_repository import (
    PriceAlertRepository
)
from app.services.portfolio_service import PortfolioService


class DashboardService:

    @staticmethod
    def get_dashboard(
        db: Session,
        current_user
    ):

        portfolio_summary = PortfolioService.get_summary(
            db,
            current_user.id
        )

        watchlist_result = (
            WatchlistRepository.get_user_watchlist(
                db=db,
                user_id=current_user.id,
                page=1,
                limit=100
            )
        )

        alerts_result = (
            PriceAlertRepository.get_user_alerts(
                db=db,
                user_id=current_user.id,
                page=1,
                limit=100
            )
        )

        watchlist_items = watchlist_result["items"]
        price_alerts = alerts_result["items"]

        return {
            "user": {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email
            },

            "portfolio": {
                "total_invested": portfolio_summary[
                    "total_invested"
                ],
                "current_value": portfolio_summary[
                    "current_value"
                ],
                "profit_loss": portfolio_summary[
                    "profit_loss"
                ],
                "return_percentage": portfolio_summary[
                    "return_percentage"
                ],
                "holdings": portfolio_summary[
                    "holdings"
                ]
            },

           "watchlist": [
    {
        "id": item.id,
        "stock_symbol": item.stock.symbol
    }
    for item in watchlist_items
],

            "price_alerts": [
                {
                    "id": alert.id,
                    "stock_symbol": alert.stock_symbol,
                    "target_price": alert.target_price,
                    "condition": alert.condition,
                    "is_triggered": alert.is_triggered
                }
                for alert in price_alerts
            ],

            "watchlist_count": watchlist_result["total"],

            "alerts_count": alerts_result["total"]
        }