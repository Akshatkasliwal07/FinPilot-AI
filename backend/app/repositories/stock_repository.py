from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.stock import Stock


class StockRepository:

    @staticmethod
    def create_stock(
        db: Session,
        stock: Stock
    ):
        try:
            db.add(stock)
            db.commit()
            db.refresh(stock)

            return stock

        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def get_stock_by_symbol(
        db: Session,
        symbol: str
    ):
        return (
            db.query(Stock)
            .filter(
                Stock.symbol == symbol.upper()
            )
            .first()
        )

    @staticmethod
    def get_all_stocks(
        db: Session,
        page: int = 1,
        limit: int = 10,
        symbol: str | None = None,
        sector: str | None = None
    ):
        query = db.query(Stock)

        if symbol:
            query = query.filter(
                Stock.symbol.ilike(
                    f"%{symbol.strip()}%"
                )
            )

        if sector:
            query = query.filter(
                Stock.sector.ilike(
                    f"%{sector.strip()}%"
                )
            )

        total = query.count()
        offset = (page - 1) * limit

        items = (
            query
            .order_by(Stock.symbol.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "items": items,
            "total": total
        }