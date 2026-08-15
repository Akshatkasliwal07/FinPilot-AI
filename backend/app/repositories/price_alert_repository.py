from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.price_alert import PriceAlert


class PriceAlertRepository:

    @staticmethod
    def create_alert(
        db: Session,
        alert: PriceAlert
    ):
        try:
            db.add(alert)
            db.commit()
            db.refresh(alert)

            return alert

        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def get_user_alerts(
        db: Session,
        user_id: int,
        page: int = 1,
        limit: int = 10,
        symbol: str | None = None
    ):
        query = (
            db.query(PriceAlert)
            .filter(
                PriceAlert.user_id == user_id
            )
        )

        if symbol:
            query = query.filter(
                PriceAlert.stock_symbol.ilike(
                    f"%{symbol.strip()}%"
                )
            )

        total = query.count()
        offset = (page - 1) * limit

        items = (
            query
            .order_by(PriceAlert.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "items": items,
            "total": total
        }

    @staticmethod
    def get_alert_by_id(
        db: Session,
        alert_id: int
    ):
        return (
            db.query(PriceAlert)
            .filter(
                PriceAlert.id == alert_id
            )
            .first()
        )

    @staticmethod
    def delete_alert(
        db: Session,
        alert: PriceAlert
    ):
        try:
            db.delete(alert)
            db.commit()

            return True

        except SQLAlchemyError:
            db.rollback()
            raise