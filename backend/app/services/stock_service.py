import math
import yfinance as yf

from sqlalchemy.orm import Session

from app.core.exceptions import FinPilotException
from app.models.stock import Stock
from app.repositories.stock_repository import StockRepository
from app.schemas.stock_schema import StockCreate


class StockService:

    # ---------------------------------
    # Create Stock
    # ---------------------------------

    @staticmethod
    def create_stock(
        db: Session,
        stock: StockCreate
    ):
        symbol = stock.symbol.strip().upper()

        existing = StockRepository.get_stock_by_symbol(
            db,
            symbol
        )

        if existing:
            raise FinPilotException(
                "Stock already exists.",
                400
            )

        new_stock = Stock(
            symbol=symbol,
            company_name=stock.company_name,
            sector=stock.sector,
            exchange=stock.exchange
        )

        return StockRepository.create_stock(
            db,
            new_stock
        )

    # ---------------------------------
    # Get Stocks with Pagination
    # ---------------------------------

    @staticmethod
    def get_all_stocks(
        db: Session,
        page: int = 1,
        limit: int = 10,
        symbol: str | None = None,
        sector: str | None = None
    ):
        result = StockRepository.get_all_stocks(
            db=db,
            page=page,
            limit=limit,
            symbol=symbol,
            sector=sector
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

    # ---------------------------------
    # Get Live Stock Data
    # ---------------------------------

    @staticmethod
    def get_live_stock(
        symbol: str
    ):
        symbol = symbol.strip().upper()

        # Indian stocks are available on
        # Yahoo Finance using .NS
        yahoo_symbol = f"{symbol}.NS"

        try:
            ticker = yf.Ticker(yahoo_symbol)

            data = ticker.history(
                period="1d",
                interval="1d",
                auto_adjust=False
            )

            if data.empty:
                raise FinPilotException(
                    "Stock not found.",
                    404
                )

            row = data.iloc[-1]

            close_price = float(row["Close"])
            open_price = float(row["Open"])
            high_price = float(row["High"])
            low_price = float(row["Low"])
            volume = int(row["Volume"])

            # Previous close
            previous_close = None

            try:
                previous_data = ticker.history(
                    period="5d",
                    interval="1d",
                    auto_adjust=False
                )

                if len(previous_data) >= 2:
                    previous_close = float(
                        previous_data.iloc[-2]["Close"]
                    )

            except Exception as e:
                print(
                    f"Previous close error for {yahoo_symbol}:",
                    e
                )

            # Fallback if previous close is unavailable
            if previous_close is None:
                previous_close = close_price

            change = close_price - previous_close

            if previous_close != 0:
                change_percent = (
                    change / previous_close
                ) * 100
            else:
                change_percent = 0

            latest_date = data.index[-1]

            return {
                "01. symbol": yahoo_symbol,
                "02. open": str(
                    round(open_price, 2)
                ),
                "03. high": str(
                    round(high_price, 2)
                ),
                "04. low": str(
                    round(low_price, 2)
                ),
                "05. price": str(
                    round(close_price, 2)
                ),
                "06. volume": str(volume),
                "07. latest trading day":
                    latest_date.strftime(
                        "%Y-%m-%d"
                    ),
                "08. previous close": str(
                    round(previous_close, 2)
                ),
                "09. change": str(
                    round(change, 2)
                ),
                "10. change percent":
                    f"{change_percent:.4f}%",
                "data_source": "Yahoo Finance"
            }

        except FinPilotException:
            raise

        except Exception as e:
            print(
                f"Live stock error for {yahoo_symbol}:",
                e
            )

            raise FinPilotException(
                "Unable to fetch live stock data.",
                500
            )

    # ---------------------------------
    # Get Historical Stock Data
    # ---------------------------------

    @staticmethod
    def get_stock_history(
        symbol: str,
        period: str = "1mo"
    ):
        symbol = symbol.strip().upper()

        # Convert application symbol
        # to Yahoo Finance symbol
        yahoo_symbol = f"{symbol}.NS"

        allowed_periods = {
            "1d": "1d",
            "5d": "5d",
            "1mo": "1mo",
            "3mo": "3mo",
            "6mo": "6mo",
            "1y": "1y",
            "2y": "2y",
            "5y": "5y",
        }

        if period not in allowed_periods:
            period = "1mo"

        try:
            ticker = yf.Ticker(yahoo_symbol)

            data = ticker.history(
                period=period,
                interval="1d",
                auto_adjust=False
            )

            if data.empty:
                raise FinPilotException(
                    "Historical stock data not found.",
                    404
                )

            history = []

            for index, row in data.iterrows():

                history.append({
                    "date": index.strftime(
                        "%Y-%m-%d"
                    ),
                    "open": round(
                        float(row["Open"]),
                        2
                    ),
                    "high": round(
                        float(row["High"]),
                        2
                    ),
                    "low": round(
                        float(row["Low"]),
                        2
                    ),
                    "close": round(
                        float(row["Close"]),
                        2
                    ),
                    "volume": int(
                        row["Volume"]
                    )
                })

            return {
                "symbol": yahoo_symbol,
                "period": period,
                "data_source": "Yahoo Finance",
                "items": history
            }

        except FinPilotException:
            raise

        except Exception as e:
            print(
                f"History error for {yahoo_symbol}:",
                e
            )

            raise FinPilotException(
                "Unable to fetch historical stock data.",
                500
            )