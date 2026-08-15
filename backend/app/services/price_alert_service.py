import math

from sqlalchemy.orm import Session

from app.core.exceptions import FinPilotException
from app.models.price_alert import PriceAlert
from app.repositories.price_alert_repository import (
    PriceAlertRepository
)
from app.schemas.price_alert_schema import (
    PriceAlertCreate
)
from app.services.stock_service import StockService


class PriceAlertService:

    # -----------------------------------------
    # Create Price Alert
    # -----------------------------------------

    @staticmethod
    def create_alert(
        db: Session,
        user_id: int,
        alert: PriceAlertCreate
    ):
        stock_symbol = alert.stock_symbol.strip().upper()
        condition = alert.condition.strip().lower()

        if not stock_symbol:
            raise FinPilotException(
                "Stock symbol is required.",
                400
            )

        if condition not in {"above", "below"}:
            raise FinPilotException(
                "Condition must be either 'above' or 'below'.",
                400
            )

        if alert.target_price <= 0:
            raise FinPilotException(
                "Target price must be greater than zero.",
                400
            )

        new_alert = PriceAlert(
            user_id=user_id,
            stock_symbol=stock_symbol,
            target_price=alert.target_price,
            condition=condition,
            is_triggered=False
        )

        return PriceAlertRepository.create_alert(
            db,
            new_alert
        )

    # -----------------------------------------
    # Get User Alerts
    # -----------------------------------------

    @staticmethod
    def get_alerts(
        db: Session,
        user_id: int,
        page: int = 1,
        limit: int = 10,
        symbol: str | None = None
    ):
        result = PriceAlertRepository.get_user_alerts(
            db=db,
            user_id=user_id,
            page=page,
            limit=limit,
            symbol=symbol
        )

        total = result["total"]

        total_pages = (
            math.ceil(total / limit)
            if total > 0
            else 0
        )

        return {
            "items": result["items"],
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }

    # -----------------------------------------
    # Delete Alert
    # -----------------------------------------

    @staticmethod
    def delete_alert(
        db: Session,
        user_id: int,
        alert_id: int
    ):
        alert = PriceAlertRepository.get_alert_by_id(
            db,
            alert_id
        )

        if not alert:
            raise FinPilotException(
                "Price alert not found.",
                404
            )

        if alert.user_id != user_id:
            raise FinPilotException(
                "You cannot delete another user's price alert.",
                403
            )

        return PriceAlertRepository.delete_alert(
            db,
            alert
        )

    # -----------------------------------------
    # Check Alert
    # -----------------------------------------

    @staticmethod
    def check_alert(
        db: Session,
        alert: PriceAlert
    ):
        """
        Check one alert against the current live stock price.
        """

        if alert.is_triggered:
            return {
                "triggered": True,
                "message": "Alert has already been triggered."
            }

        try:
            live_data = StockService.get_live_stock(
                alert.stock_symbol
            )

            live_price = float(
                live_data["05. price"]
            )

        except FinPilotException:
            raise

        except Exception as exc:
            print(
                f"Price alert check error for "
                f"{alert.stock_symbol}:",
                exc
            )

            raise FinPilotException(
                "Unable to fetch current stock price.",
                500
            )

        triggered = False

        # -----------------------------------------
        # Above condition
        # -----------------------------------------

        if alert.condition == "above":
            if live_price >= alert.target_price:
                triggered = True

        # -----------------------------------------
        # Below condition
        # -----------------------------------------

        elif alert.condition == "below":
            if live_price <= alert.target_price:
                triggered = True

        # -----------------------------------------
        # Update database
        # -----------------------------------------

        if triggered:

            alert.is_triggered = True

            db.commit()
            db.refresh(alert)

            return {
                "triggered": True,
                "message": (
                    f"{alert.stock_symbol} has reached "
                    f"your target price."
                ),
                "stock_symbol": alert.stock_symbol,
                "current_price": live_price,
                "target_price": alert.target_price,
                "condition": alert.condition
            }

        return {
            "triggered": False,
            "message": "Target price has not been reached.",
            "stock_symbol": alert.stock_symbol,
            "current_price": live_price,
            "target_price": alert.target_price,
            "condition": alert.condition
        }

    # -----------------------------------------
    # Check All Active Alerts For User
    # -----------------------------------------

    @staticmethod
    def check_user_alerts(
        db: Session,
        user_id: int
    ):
        result = PriceAlertRepository.get_user_alerts(
            db=db,
            user_id=user_id,
            page=1,
            limit=100
        )

        alerts = result["items"]

        results = []

        for alert in alerts:

            if alert.is_triggered:
                continue

            try:
                result = PriceAlertService.check_alert(
                    db,
                    alert
                )

                results.append(result)

            except FinPilotException as exc:

                results.append({
                    "triggered": False,
                    "stock_symbol": alert.stock_symbol,
                    "error": str(exc)
                })

        return {
            "checked": len(alerts),
            "results": results
        }