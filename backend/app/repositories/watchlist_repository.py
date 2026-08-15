from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.watchlist import Watchlist
from app.models.stock import Stock


class WatchlistRepository:

    # -----------------------------------------
    # Create Watchlist Item
    # -----------------------------------------

    @staticmethod
    def create_watchlist(
        db: Session,
        watchlist: Watchlist
    ):
        try:
            db.add(watchlist)
            db.commit()
            db.refresh(watchlist)

            return watchlist

        except SQLAlchemyError:
            db.rollback()
            raise

    # -----------------------------------------
    # Get User Watchlist
    # -----------------------------------------

    @staticmethod
    def get_user_watchlist(
        db: Session,
        user_id: int,
        page: int = 1,
        limit: int = 10,
        symbol: str | None = None
    ):
        query = (
            db.query(Watchlist)
            .join(
                Stock,
                Watchlist.stock_id == Stock.id
            )
            .filter(
                Watchlist.user_id == user_id
            )
        )

        if symbol:
            query = query.filter(
                Stock.symbol.ilike(
                    f"%{symbol.strip()}%"
                )
            )

        total = query.count()

        offset = (page - 1) * limit

        items = (
            query
            .order_by(
                Watchlist.created_at.desc()
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "items": items,
            "total": total
        }

    # -----------------------------------------
    # Find Watchlist By User + Stock
    # -----------------------------------------

    @staticmethod
    def get_by_user_and_stock(
        db: Session,
        user_id: int,
        stock_id: int
    ):
        return (
            db.query(Watchlist)
            .filter(
                Watchlist.user_id == user_id,
                Watchlist.stock_id == stock_id
            )
            .first()
        )

    # -----------------------------------------
    # Find Stock By Symbol
    # -----------------------------------------

    @staticmethod
    def get_stock_by_symbol(
        db: Session,
        stock_symbol: str
    ):
        return (
            db.query(Stock)
            .filter(
                Stock.symbol == stock_symbol.upper()
            )
            .first()
        )

    # -----------------------------------------
    # Get Watchlist Item By ID
    # -----------------------------------------

    @staticmethod
    def get_watchlist_by_id(
        db: Session,
        watchlist_id: int
    ):
        return (
            db.query(Watchlist)
            .filter(
                Watchlist.id == watchlist_id
            )
            .first()
        )

    # -----------------------------------------
    # Delete Watchlist Item
    # -----------------------------------------

    @staticmethod
    def delete_watchlist(
        db: Session,
        watchlist: Watchlist
    ):
        try:
            db.delete(watchlist)
            db.commit()

            return True

        except SQLAlchemyError:
            db.rollback()
            raise