from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.repositories.portfolio_repository import PortfolioRepository
from app.schemas.portfolio_schema import PortfolioCreate
from app.core.exceptions import FinPilotException
from app.api.alpha_vantage import AlphaVantageAPI


class PortfolioService:

    @staticmethod
    def add_stock(
        db: Session,
        user_id: int,
        portfolio: PortfolioCreate
    ):

        if portfolio.quantity <= 0:
            raise FinPilotException(
                "Quantity must be greater than zero.",
                400
            )

        if portfolio.purchase_price <= 0:
            raise FinPilotException(
                "Purchase price must be greater than zero.",
                400
            )

        new_portfolio = Portfolio(
            user_id=user_id,
            stock_symbol=portfolio.stock_symbol.upper(),
            quantity=portfolio.quantity,
            purchase_price=portfolio.purchase_price
        )

        return PortfolioRepository.create_portfolio(
            db,
            new_portfolio
        )

    @staticmethod
    def get_portfolio(
        db: Session,
        user_id: int
    ):

        return PortfolioRepository.get_user_portfolio(
            db,
            user_id
        )

    @staticmethod
    def delete_stock(
        db: Session,
        user_id: int,
        portfolio_id: int
    ):

        portfolio = PortfolioRepository.get_portfolio_by_id(
            db,
            portfolio_id
        )

        if not portfolio:
            raise FinPilotException(
                "Portfolio item not found.",
                404
            )

        if portfolio.user_id != user_id:
            raise FinPilotException(
                "You cannot delete another user's portfolio.",
                403
            )

        return PortfolioRepository.delete_portfolio(
            db,
            portfolio
        )

    @staticmethod
    def get_summary(
        db: Session,
        user_id: int
    ):

        portfolio_items = PortfolioRepository.get_user_portfolio(
            db,
            user_id
        )

        if not portfolio_items:
            return {
                "total_invested": 0,
                "current_value": 0,
                "profit_loss": 0,
                "return_percentage": 0,
                "holdings": 0,
                "items": []
            }

        total_invested = 0
        current_value = 0
        items = []

        for item in portfolio_items:

            quote = AlphaVantageAPI.get_stock_quote(
                item.stock_symbol
            )

            if not quote:
                raise FinPilotException(
                    f"Live price not found for {item.stock_symbol}.",
                    404
                )

            live_price = float(
                quote["05. price"]
            )

            invested_amount = (
                item.quantity * item.purchase_price
            )

            market_value = (
                item.quantity * live_price
            )

            profit_loss = (
                market_value - invested_amount
            )

            return_percentage = (
                (profit_loss / invested_amount) * 100
                if invested_amount > 0 else 0
            )

            total_invested += invested_amount
            current_value += market_value

            items.append({
                "id": item.id,
                "stock_symbol": item.stock_symbol,
                "quantity": item.quantity,
                "purchase_price": round(item.purchase_price, 2),
                "live_price": round(live_price, 2),
                "invested_amount": round(invested_amount, 2),
                "current_value": round(market_value, 2),
                "profit_loss": round(profit_loss, 2),
                "return_percentage": round(return_percentage, 2)
            })

        total_profit_loss = (
            current_value - total_invested
        )

        total_return_percentage = (
            (total_profit_loss / total_invested) * 100
            if total_invested > 0 else 0
        )

        return {
            "total_invested": round(total_invested, 2),
            "current_value": round(current_value, 2),
            "profit_loss": round(total_profit_loss, 2),
            "return_percentage": round(total_return_percentage, 2),
            "holdings": len(portfolio_items),
            "items": items
        }