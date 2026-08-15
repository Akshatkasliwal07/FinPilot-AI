from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio


class PortfolioRepository:

    @staticmethod
    def create_portfolio(
        db: Session,
        portfolio: Portfolio
    ):
        try:
            db.add(portfolio)
            db.commit()
            db.refresh(portfolio)

            return portfolio

        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def get_user_portfolio(
        db: Session,
        user_id: int
    ):
        return (
            db.query(Portfolio)
            .filter(
                Portfolio.user_id == user_id
            )
            .all()
        )

    @staticmethod
    def get_portfolio_by_id(
        db: Session,
        portfolio_id: int
    ):
        return (
            db.query(Portfolio)
            .filter(
                Portfolio.id == portfolio_id
            )
            .first()
        )

    @staticmethod
    def delete_portfolio(
        db: Session,
        portfolio: Portfolio
    ):
        try:
            db.delete(portfolio)
            db.commit()

            return True

        except SQLAlchemyError:
            db.rollback()
            raise