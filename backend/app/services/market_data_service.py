from sqlalchemy.orm import Session
import yfinance as yf

from app.models.market_data import (
    MarketInstrument,
    Exchange,
)

from app.providers.eodhd_provider import (
    EODHDProvider,
)

from app.repositories.market_data_repository import (
    MarketDataRepository,
)


# ============================================================
# FINPILOT MARKET SCOPE
# INDIA ONLY
# ============================================================

INDIAN_EXCHANGES = {
    "NSE": {
        "name": "National Stock Exchange of India",
        "country": "India",
        "currency": "INR",
    },
    "BSE": {
        "name": "BSE India",
        "country": "India",
        "currency": "INR",
    },
}


class MarketDataService:

    # ========================================================
    # SEARCH INDIAN STOCKS
    # LOCAL DATABASE + DYNAMIC YAHOO FINANCE FALLBACK
    # ========================================================

    @staticmethod
    def search(
        db: Session,
        query: str,
        limit: int = 20,
    ):
        """
        Search ANY Indian NSE/BSE stock.

        Local database is used first. If the stock is not present
        locally, Yahoo Finance is queried dynamically.

        Only NSE (.NS) and BSE (.BO) results are returned.
        No hard-coded stock list is used.
        """

        query = (
            query.strip()
            if query
            else ""
        )

        if not query:
            return []

        limit = max(1, min(int(limit), 100))
        query_upper = query.upper()

        result = []
        seen = set()

        # ----------------------------------------------------
        # 1. LOCAL DATABASE
        # ----------------------------------------------------

        try:
            instruments = (
                MarketDataRepository.search_instruments(
                    db,
                    query_upper,
                    limit,
                )
            )
        except Exception:
            instruments = []

        for item in instruments or []:

            country = str(
                item.country or ""
            ).upper()

            currency = str(
                item.currency or ""
            ).upper()

            if (
                country != "INDIA"
                and "INDIA" not in country
                and currency != "INR"
            ):
                continue

            symbol = str(
                item.symbol or ""
            ).strip().upper()

            if not symbol:
                continue

            # Keep the DB result only if it is clearly Indian.
            # Existing imported NSE/BSE records may not contain
            # the Yahoo suffix, so the database exchange_id is
            # retained for the frontend.
            if symbol in seen:
                continue

            seen.add(symbol)

            result.append(
                {
                    "id": item.id,
                    "symbol": symbol,
                    "name": (
                        item.name
                        or symbol
                    ),
                    "instrument_type": (
                        item.instrument_type
                    ),
                    "exchange_id": (
                        item.exchange_id
                    ),
                    "exchange": None,
                    "currency": (
                        item.currency
                        or "INR"
                    ),
                    "country": "India",
                    "sector": item.sector,
                    "industry": item.industry,
                    "logo_url": item.logo_url,
                    "data_source": "Database",
                }
            )

            if len(result) >= limit:
                return result[:limit]

        # ----------------------------------------------------
        # 2. DYNAMIC YAHOO FINANCE SEARCH
        # ----------------------------------------------------

        try:
            search = yf.Search(
                query,
                max_results=max(
                    8,
                    min(limit * 2, 20),
                ),
                news_count=0,
                lists_count=0,
                include_cb=False,
                include_nav_links=False,
                include_research=False,
                include_cultural_assets=False,
                enable_fuzzy_query=True,
                recommended=0,
                timeout=15,
                raise_errors=False,
            )

            quotes = getattr(
                search,
                "quotes",
                None,
            ) or []

        except Exception:
            quotes = []

        # ----------------------------------------------------
        # 3. FILTER ONLY NSE / BSE
        # ----------------------------------------------------

        for item in quotes:

            if not isinstance(item, dict):
                continue

            yahoo_symbol = str(
                item.get("symbol")
                or ""
            ).strip().upper()

            if not yahoo_symbol:
                continue

            if yahoo_symbol.endswith(".NS"):
                exchange = "NSE"
            elif yahoo_symbol.endswith(".BO"):
                exchange = "BSE"
            else:
                continue

            base_symbol = yahoo_symbol.rsplit(
                ".",
                1,
            )[0]

            if not base_symbol:
                continue

            if base_symbol in seen:
                continue

            quote_type = str(
                item.get("quoteType")
                or item.get("typeDisp")
                or ""
            ).lower().replace(" ", "")

            blocked_types = {
                "etf",
                "index",
                "currency",
                "mutualfund",
                "fund",
                "future",
                "option",
                "crypto",
            }

            if quote_type in blocked_types:
                continue

            name = (
                item.get("longname")
                or item.get("longName")
                or item.get("shortname")
                or item.get("shortName")
                or base_symbol
            )

            seen.add(base_symbol)

            result.append(
                {
                    "id": None,
                    "symbol": base_symbol,
                    "name": str(name),
                    "instrument_type": "Common Stock",
                    "exchange_id": None,
                    "exchange": exchange,
                    "currency": "INR",
                    "country": "India",
                    "sector": None,
                    "industry": None,
                    "logo_url": None,
                    "yahoo_symbol": yahoo_symbol,
                    "data_source": "Yahoo Finance",
                }
            )

            if len(result) >= limit:
                break

        return result


    # ========================================================
    # LOCAL QUOTE
    # ========================================================

    @staticmethod
    def get_quote(
        db: Session,
        symbol: str,
    ):

        symbol = symbol.strip().upper()

        instrument = (
            MarketDataRepository.get_instrument(
                db,
                symbol,
            )
        )

        if not instrument:
            return None

        quote = (
            MarketDataRepository.get_quote(
                db,
                instrument.id,
            )
        )

        return {
            "instrument": {
                "id": instrument.id,
                "symbol": instrument.symbol,
                "name": instrument.name,
                "type": instrument.instrument_type,
                "exchange_id": (
                    instrument.exchange_id
                ),
                "currency": instrument.currency,
                "country": instrument.country,
                "sector": instrument.sector,
                "industry": instrument.industry,
                "logo_url": instrument.logo_url,
            },
            "quote": (
                {
                    "price": quote.price,
                    "open": quote.open,
                    "high": quote.high,
                    "low": quote.low,
                    "previous_close": (
                        quote.previous_close
                    ),
                    "change": quote.change,
                    "change_percent": (
                        quote.change_percent
                    ),
                    "volume": quote.volume,
                    "market_cap": quote.market_cap,
                    "bid": quote.bid,
                    "ask": quote.ask,
                    "fifty_two_week_high": (
                        quote.fifty_two_week_high
                    ),
                    "fifty_two_week_low": (
                        quote.fifty_two_week_low
                    ),
                    "market_status": (
                        quote.market_status
                    ),
                    "quote_time": quote.quote_time,
                    "data_source": quote.data_source,
                }
                if quote
                else None
            ),
        }

    # ========================================================
    # LOCAL PRICE HISTORY
    # ========================================================

    @staticmethod
    def get_history(
        db: Session,
        symbol: str,
        timeframe: str = "1d",
        limit: int = 365,
    ):

        symbol = symbol.strip().upper()

        instrument = (
            MarketDataRepository.get_instrument(
                db,
                symbol,
            )
        )

        if not instrument:
            return None

        history = (
            MarketDataRepository.get_history(
                db,
                instrument.id,
                timeframe,
                limit,
            )
        )

        history.reverse()

        return [
            {
                "time": item.candle_time,
                "open": item.open,
                "high": item.high,
                "low": item.low,
                "close": item.close,
                "adjusted_close": (
                    item.adjusted_close
                ),
                "volume": item.volume,
            }
            for item in history
        ]

    # ========================================================
    # LOCAL FUNDAMENTALS
    # ========================================================

    @staticmethod
    def get_fundamentals(
        db: Session,
        symbol: str,
    ):

        symbol = symbol.strip().upper()

        instrument = (
            MarketDataRepository.get_instrument(
                db,
                symbol,
            )
        )

        if not instrument:
            return None

        fundamentals = (
            MarketDataRepository.get_fundamentals(
                db,
                instrument.id,
            )
        )

        return [
            {
                "market_cap": item.market_cap,
                "enterprise_value": (
                    item.enterprise_value
                ),
                "revenue": item.revenue,
                "net_income": item.net_income,
                "gross_profit": item.gross_profit,
                "operating_income": (
                    item.operating_income
                ),
                "total_assets": (
                    item.total_assets
                ),
                "total_liabilities": (
                    item.total_liabilities
                ),
                "total_equity": (
                    item.total_equity
                ),
                "cash": item.cash,
                "debt": item.debt,
                "eps": item.eps,
                "book_value_per_share": (
                    item.book_value_per_share
                ),
                "dividend_per_share": (
                    item.dividend_per_share
                ),
                "dividend_yield": (
                    item.dividend_yield
                ),
                "pe_ratio": item.pe_ratio,
                "pb_ratio": item.pb_ratio,
                "ps_ratio": item.ps_ratio,
                "roe": item.roe,
                "roa": item.roa,
                "debt_to_equity": (
                    item.debt_to_equity
                ),
                "fiscal_year": item.fiscal_year,
                "fiscal_quarter": (
                    item.fiscal_quarter
                ),
                "report_date": item.report_date,
            }
            for item in fundamentals
        ]

    # ========================================================
    # LOCAL TECHNICALS
    # ========================================================

    @staticmethod
    def get_technicals(
        db: Session,
        symbol: str,
        timeframe: str = "1d",
    ):

        symbol = symbol.strip().upper()

        instrument = (
            MarketDataRepository.get_instrument(
                db,
                symbol,
            )
        )

        if not instrument:
            return None

        item = (
            MarketDataRepository.get_technicals(
                db,
                instrument.id,
                timeframe,
            )
        )

        if not item:
            return None

        return {
            "timeframe": item.timeframe,
            "calculation_time": (
                item.calculation_time
            ),
            "sma_20": item.sma_20,
            "sma_50": item.sma_50,
            "sma_200": item.sma_200,
            "ema_20": item.ema_20,
            "ema_50": item.ema_50,
            "ema_200": item.ema_200,
            "rsi_14": item.rsi_14,
            "macd": item.macd,
            "macd_signal": item.macd_signal,
            "macd_histogram": (
                item.macd_histogram
            ),
            "bollinger_upper": (
                item.bollinger_upper
            ),
            "bollinger_middle": (
                item.bollinger_middle
            ),
            "bollinger_lower": (
                item.bollinger_lower
            ),
            "volatility": item.volatility,
            "support": item.support,
            "resistance": item.resistance,
        }

    # ========================================================
    # LOCAL NEWS
    # ========================================================

    @staticmethod
    def get_news(
        db: Session,
        symbol: str,
        limit: int = 20,
    ):

        symbol = symbol.strip().upper()

        instrument = (
            MarketDataRepository.get_instrument(
                db,
                symbol,
            )
        )

        if not instrument:
            return None

        news = (
            MarketDataRepository.get_news(
                db,
                instrument.id,
                limit,
            )
        )

        return [
            {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "url": item.url,
                "image_url": item.image_url,
                "source": item.source,
                "sentiment": item.sentiment,
                "sentiment_score": (
                    item.sentiment_score
                ),
                "published_at": (
                    item.published_at
                ),
            }
            for item in news
        ]

    # ========================================================
    # YAHOO FINANCE SYMBOL
    # ========================================================

    @staticmethod
    def get_yahoo_symbol(
        symbol: str,
        exchange: str = "NSE",
    ) -> str:

        symbol = symbol.strip().upper()
        exchange = exchange.strip().upper()

        # Remove existing Yahoo suffix
        if symbol.endswith(".NS"):
            return symbol

        if symbol.endswith(".BO"):
            return symbol

        if exchange == "BSE":
            return f"{symbol}.BO"

        # Default = NSE
        return f"{symbol}.NS"

    # ========================================================
    # YAHOO FINANCE QUOTE
    # ========================================================

    @staticmethod
    def get_from_yfinance(
        symbol: str,
        exchange: str = "NSE",
    ):

        yahoo_symbol = (
            MarketDataService.get_yahoo_symbol(
                symbol,
                exchange,
            )
        )

        try:

            ticker = yf.Ticker(
                yahoo_symbol
            )

            data = ticker.history(
                period="5d",
                auto_adjust=False,
            )

        except Exception as exc:

            raise RuntimeError(
                f"Yahoo Finance error for "
                f"{yahoo_symbol}: {exc}"
            )

        if data is None or data.empty:
            return None

        # Remove rows without closing prices
        data = data.dropna(
            subset=["Close"]
        )

        if data.empty:
            return None

        latest = data.iloc[-1]

        price = float(
            latest["Close"]
        )

        open_price = float(
            latest["Open"]
        )

        high = float(
            latest["High"]
        )

        low = float(
            latest["Low"]
        )

        volume = int(
            latest["Volume"]
        )

        previous_close = None

        if len(data) >= 2:

            previous_close = float(
                data["Close"].iloc[-2]
            )

        if (
            previous_close is not None
            and previous_close != 0
        ):

            change = (
                price
                - previous_close
            )

            change_percent = (
                change
                / previous_close
            ) * 100

        else:

            change = 0.0
            change_percent = 0.0

        trading_day = str(
            data.index[-1].date()
        )

        return {
            "01. symbol": yahoo_symbol,

            "02. open": str(
                round(
                    open_price,
                    2,
                )
            ),

            "03. high": str(
                round(
                    high,
                    2,
                )
            ),

            "04. low": str(
                round(
                    low,
                    2,
                )
            ),

            "05. price": str(
                round(
                    price,
                    2,
                )
            ),

            "06. volume": str(
                volume
            ),

            "07. latest trading day": (
                trading_day
            ),

            "08. previous close": (
                str(
                    round(
                        previous_close,
                        2,
                    )
                )
                if previous_close is not None
                else None
            ),

            "09. change": str(
                round(
                    change,
                    2,
                )
            ),

            "10. change percent": (
                str(
                    round(
                        change_percent,
                        2,
                    )
                )
                + "%"
            ),

            # Additional normalized fields
            "symbol": symbol.upper(),

            "price": price,

            "open": open_price,

            "high": high,

            "low": low,

            "volume": volume,

            "previous_close": (
                previous_close
            ),

            "change": change,

            "change_percent": (
                change_percent
            ),

            "timestamp": (
                trading_day
            ),

            "market_status": (
                "latest_available"
            ),

            "data_source": (
                "Yahoo Finance"
            ),
        }

    # ========================================================
    # YAHOO FINANCE HISTORY
    # ========================================================

    @staticmethod
    def get_history_from_yfinance(
        symbol: str,
        from_date: str | None = None,
        to_date: str | None = None,
        period: str = "d",
        exchange: str = "NSE",
    ):

        yahoo_symbol = (
            MarketDataService.get_yahoo_symbol(
                symbol,
                exchange,
            )
        )

        try:

            ticker = yf.Ticker(
                yahoo_symbol
            )

            if from_date or to_date:

                data = ticker.history(
                    start=from_date,
                    end=to_date,
                    auto_adjust=False,
                )

            else:

                # Default historical window
                data = ticker.history(
                    period="1y",
                    auto_adjust=False,
                )

        except Exception as exc:

            raise RuntimeError(
                f"Yahoo Finance history error "
                f"for {yahoo_symbol}: {exc}"
            )

        if data is None or data.empty:
            return []

        result = []

        for index, row in data.iterrows():

            close = row.get(
                "Close"
            )

            if close is None:
                continue

            try:

                close_value = float(
                    close
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            result.append(
                {
                    "date": str(
                        index.date()
                    ),

                    "time": str(
                        index.date()
                    ),

                    "open": float(
                        row["Open"]
                    ),

                    "high": float(
                        row["High"]
                    ),

                    "low": float(
                        row["Low"]
                    ),

                    "close": close_value,

                    "adjusted_close": float(
                        row.get(
                            "Adj Close",
                            close_value,
                        )
                    ),

                    "volume": int(
                        row.get(
                            "Volume",
                            0,
                        )
                    ),
                }
            )

        return result

    # ========================================================
    # IMPORT EXCHANGE INSTRUMENTS
    # ========================================================

    @staticmethod
    def import_exchange_instruments(
        db: Session,
        exchange_code: str,
        batch_size: int = 1000,
    ):

        exchange_code = (
            exchange_code.strip().upper()
        )

        if exchange_code not in (
            "NSE",
            "BSE",
        ):
            raise ValueError(
                "FinPilot supports only "
                "Indian exchanges: NSE and BSE."
            )

        if batch_size < 50:
            batch_size = 50

        if batch_size > 2000:
            batch_size = 2000

        exchange = (
            db.query(Exchange)
            .filter(
                Exchange.code
                == exchange_code
            )
            .first()
        )

        if not exchange:
            raise ValueError(
                f"Exchange '{exchange_code}' "
                f"was not found in the database."
            )

        exchange_id = exchange.id

        # ----------------------------------------------------
        # EODHD import is retained for database population.
        # Quote data does NOT use EODHD anymore.
        # ----------------------------------------------------

        instruments = (
            EODHDProvider
            .get_exchange_symbols(
                exchange_code
            )
        )

        if not instruments:
            return {
                "exchange": exchange_code,
                "exchange_id": exchange_id,
                "inserted": 0,
                "updated": 0,
                "total": 0,
            }

        inserted = 0
        updated = 0
        processed = 0

        for item in instruments:

            symbol = item.get(
                "Code"
            )

            if not symbol:
                continue

            symbol = str(
                symbol
            ).strip().upper()

            existing = (
                MarketDataRepository
                .get_instrument(
                    db,
                    symbol,
                )
            )

            data = {
                "symbol": symbol,

                "name": (
                    item.get("Name")
                    or item.get(
                        "Description"
                    )
                    or symbol
                ),

                "instrument_type": (
                    item.get("Type")
                    or "Common Stock"
                ),

                "exchange_id": exchange_id,

                "currency": (
                    item.get("Currency")
                    or "INR"
                ),

                "country": "India",

                "sector": item.get(
                    "Sector"
                ),

                "industry": item.get(
                    "Industry"
                ),

                "logo_url": None,
            }

            if existing:

                existing.name = (
                    data["name"]
                )

                existing.instrument_type = (
                    data[
                        "instrument_type"
                    ]
                )

                existing.exchange_id = (
                    data[
                        "exchange_id"
                    ]
                )

                existing.currency = (
                    data["currency"]
                )

                existing.country = (
                    data["country"]
                )

                existing.sector = (
                    data["sector"]
                )

                existing.industry = (
                    data["industry"]
                )

                existing.logo_url = (
                    data["logo_url"]
                )

                updated += 1

            else:

                instrument = (
                    MarketInstrument(
                        symbol=data[
                            "symbol"
                        ],

                        name=data[
                            "name"
                        ],

                        instrument_type=data[
                            "instrument_type"
                        ],

                        exchange_id=data[
                            "exchange_id"
                        ],

                        currency=data[
                            "currency"
                        ],

                        country=data[
                            "country"
                        ],

                        sector=data[
                            "sector"
                        ],

                        industry=data[
                            "industry"
                        ],

                        logo_url=data[
                            "logo_url"
                        ],
                    )
                )

                db.add(
                    instrument
                )

                inserted += 1

            processed += 1

            if (
                processed
                % batch_size
                == 0
            ):
                db.commit()

        db.commit()

        return {
            "exchange": exchange_code,
            "exchange_id": exchange_id,
            "inserted": inserted,
            "updated": updated,
            "total": (
                inserted
                + updated
            ),
        }

    # ========================================================
    # PROVIDER QUOTE
    # YAHOO FINANCE
    # ========================================================

    @staticmethod
    def provider_quote(
        symbol: str,
    ):

        return (
            MarketDataService
            .get_from_yfinance(
                symbol
            )
        )

    # ========================================================
    # PROVIDER HISTORY
    # YAHOO FINANCE
    # ========================================================

    @staticmethod
    def provider_history(
        symbol: str,
        from_date: str | None = None,
        to_date: str | None = None,
        period: str = "d",
    ):

        return (
            MarketDataService
            .get_history_from_yfinance(
                symbol=symbol,
                from_date=from_date,
                to_date=to_date,
                period=period,
            )
        )

    # ========================================================
    # PROVIDER FUNDAMENTALS
    # EODHD
    # ========================================================

    @staticmethod
    def provider_fundamentals(
        symbol: str,
    ):

        return (
            EODHDProvider
            .get_fundamentals(
                symbol
            )
        )

    # ========================================================
    # PROVIDER NEWS
    # EODHD
    # ========================================================

    @staticmethod
    def provider_news(
        symbol: str | None = None,
        limit: int = 20,
    ):

        return (
            EODHDProvider
            .get_news(
                symbol,
                limit,
            )
        )

    # ========================================================
    # PROVIDER SEARCH
    # EODHD
    # ========================================================

    @staticmethod
    def provider_search(
        query: str,
    ):

        return (
            EODHDProvider
            .search(
                query
            )
        )

    # ========================================================
    # PROVIDER EXCHANGE SYMBOLS
    # EODHD
    # ========================================================

    @staticmethod
    def provider_exchange_symbols(
        exchange_code: str,
    ):

        return (
            EODHDProvider
            .get_exchange_symbols(
                exchange_code
            )
        )

    # ========================================================
    # PROVIDER EXCHANGES
    # EODHD
    # ========================================================

    @staticmethod
    def provider_exchanges():

        return (
            EODHDProvider
            .get_exchanges()
        )