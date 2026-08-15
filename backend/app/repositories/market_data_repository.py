from datetime import datetime

from sqlalchemy.orm import Session

from app.models.market_data import (
    Exchange,
    MarketInstrument,
    MarketQuote,
    PriceHistory,
    Fundamental,
)


class MarketDataRepository:

    # ============================================================
    # EXCHANGE
    # ============================================================

    @staticmethod
    def get_exchange(
        db: Session,
        code: str,
    ):
        return (
            db.query(Exchange)
            .filter(
                Exchange.code == code.upper()
            )
            .first()
        )

    @staticmethod
    def create_exchange(
        db: Session,
        data: dict,
    ):
        exchange = Exchange(
            code=data["code"].upper(),
            name=data["name"],
            country=data.get("country"),
            country_code=data.get("country_code"),
            timezone=data.get("timezone"),
            currency=data.get("currency"),
            mic=data.get("mic"),
            is_active=data.get(
                "is_active",
                True,
            ),
        )

        db.add(exchange)
        db.commit()
        db.refresh(exchange)

        return exchange

    # ============================================================
    # INSTRUMENT
    # ============================================================

    @staticmethod
    def get_instrument(
        db: Session,
        symbol: str,
        exchange_id: int | None = None,
    ):
        query = (
            db.query(MarketInstrument)
            .filter(
                MarketInstrument.symbol.ilike(
                    symbol
                ),
                MarketInstrument.is_active.is_(True),
            )
        )

        if exchange_id:
            query = query.filter(
                MarketInstrument.exchange_id
                == exchange_id
            )

        return query.first()

    @staticmethod
    def create_or_update_instrument(
        db: Session,
        data: dict,
    ):
        instrument = MarketDataRepository.get_instrument(
            db,
            data["symbol"],
            data.get("exchange_id"),
        )

        if not instrument:

            instrument = MarketInstrument(
                symbol=data["symbol"],
                name=data["name"],
                instrument_type=data.get(
                    "instrument_type",
                    "STOCK",
                ),
                exchange_id=data.get(
                    "exchange_id"
                ),
                isin=data.get("isin"),
                cusip=data.get("cusip"),
                currency=data.get("currency"),
                country=data.get("country"),
                sector=data.get("sector"),
                industry=data.get("industry"),
                description=data.get("description"),
                website=data.get("website"),
                logo_url=data.get("logo_url"),
                is_active=True,
            )

            db.add(instrument)

        else:

            instrument.name = data["name"]

            for field in [
                "instrument_type",
                "isin",
                "cusip",
                "currency",
                "country",
                "sector",
                "industry",
                "description",
                "website",
                "logo_url",
            ]:

                value = data.get(field)

                if value is not None:
                    setattr(
                        instrument,
                        field,
                        value,
                    )

        db.commit()
        db.refresh(instrument)

        return instrument

    # ============================================================
    # QUOTE
    # ============================================================

    @staticmethod
    def upsert_quote(
        db: Session,
        instrument_id: int,
        data: dict,
    ):

        quote = (
            db.query(MarketQuote)
            .filter(
                MarketQuote.instrument_id
                == instrument_id
            )
            .first()
        )

        if not quote:

            quote = MarketQuote(
                instrument_id=instrument_id
            )

            db.add(quote)

        for field in [
            "price",
            "open",
            "high",
            "low",
            "previous_close",
            "change",
            "change_percent",
            "volume",
            "market_cap",
            "bid",
            "ask",
            "fifty_two_week_high",
            "fifty_two_week_low",
            "market_status",
            "currency",
            "data_source",
            "quote_time",
        ]:

            value = data.get(field)

            if value is not None:
                setattr(
                    quote,
                    field,
                    value,
                )

        quote.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(quote)

        return quote

    # ============================================================
    # HISTORICAL PRICES
    # ============================================================

    @staticmethod
    def save_price_history(
        db: Session,
        instrument_id: int,
        candles: list[dict],
        timeframe: str = "1d",
        data_source: str = "EODHD",
    ):

        saved = 0

        for candle in candles:

            candle_time = candle.get(
                "candle_time"
            )

            if not candle_time:
                continue

            existing = (
                db.query(PriceHistory)
                .filter(
                    PriceHistory.instrument_id
                    == instrument_id,
                    PriceHistory.timeframe
                    == timeframe,
                    PriceHistory.candle_time
                    == candle_time,
                )
                .first()
            )

            if existing:

                existing.open = candle.get(
                    "open",
                    existing.open,
                )

                existing.high = candle.get(
                    "high",
                    existing.high,
                )

                existing.low = candle.get(
                    "low",
                    existing.low,
                )

                existing.close = candle.get(
                    "close",
                    existing.close,
                )

                existing.adjusted_close = candle.get(
                    "adjusted_close",
                    existing.adjusted_close,
                )

                existing.volume = candle.get(
                    "volume",
                    existing.volume,
                )

                continue

            item = PriceHistory(
                instrument_id=instrument_id,
                timeframe=timeframe,
                candle_time=candle_time,
                open=candle["open"],
                high=candle["high"],
                low=candle["low"],
                close=candle["close"],
                adjusted_close=candle.get(
                    "adjusted_close"
                ),
                volume=candle.get(
                    "volume"
                ),
                data_source=data_source,
            )

            db.add(item)
            saved += 1

        db.commit()

        return saved

    # ============================================================
    # FUNDAMENTALS
    # ============================================================

    @staticmethod
    def save_fundamental(
        db: Session,
        instrument_id: int,
        data: dict,
    ):

        fiscal_year = data.get(
            "fiscal_year"
        )

        fiscal_quarter = data.get(
            "fiscal_quarter"
        )

        existing = (
            db.query(Fundamental)
            .filter(
                Fundamental.instrument_id
                == instrument_id,
                Fundamental.fiscal_year
                == fiscal_year,
                Fundamental.fiscal_quarter
                == fiscal_quarter,
            )
            .first()
        )

        if not existing:

            existing = Fundamental(
                instrument_id=instrument_id,
                fiscal_year=fiscal_year,
                fiscal_quarter=fiscal_quarter,
            )

            db.add(existing)

        fields = [
            "market_cap",
            "enterprise_value",
            "revenue",
            "net_income",
            "gross_profit",
            "operating_income",
            "total_assets",
            "total_liabilities",
            "total_equity",
            "cash",
            "debt",
            "eps",
            "book_value_per_share",
            "dividend_per_share",
            "dividend_yield",
            "pe_ratio",
            "pb_ratio",
            "ps_ratio",
            "roe",
            "roa",
            "debt_to_equity",
            "report_date",
            "data_source",
        ]

        for field in fields:

            value = data.get(field)

            if value is not None:
                setattr(
                    existing,
                    field,
                    value,
                )

        existing.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(existing)

        return existing

    # ============================================================
    # SEARCH
    # ============================================================

    @staticmethod
    def search_instruments(
        db: Session,
        query: str,
        limit: int = 20,
    ):
        from sqlalchemy import or_

        search = f"%{query}%"

        return (
            db.query(MarketInstrument)
            .filter(
                MarketInstrument.is_active.is_(True),
                or_(
                    MarketInstrument.symbol.ilike(
                        search
                    ),
                    MarketInstrument.name.ilike(
                        search
                    ),
                ),
            )
            .order_by(
                MarketInstrument.symbol
            )
            .limit(limit)
            .all()
        )

    # ============================================================
    # EXISTING READ METHODS
    # ============================================================

    @staticmethod
    def get_quote(
        db: Session,
        instrument_id: int,
    ):
        return (
            db.query(MarketQuote)
            .filter(
                MarketQuote.instrument_id
                == instrument_id
            )
            .first()
        )

    @staticmethod
    def get_history(
        db: Session,
        instrument_id: int,
        timeframe: str = "1d",
        limit: int = 365,
    ):
        return (
            db.query(PriceHistory)
            .filter(
                PriceHistory.instrument_id
                == instrument_id,
                PriceHistory.timeframe
                == timeframe,
            )
            .order_by(
                PriceHistory.candle_time.desc()
            )
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_fundamentals(
        db: Session,
        instrument_id: int,
    ):
        return (
            db.query(Fundamental)
            .filter(
                Fundamental.instrument_id
                == instrument_id
            )
            .order_by(
                Fundamental.report_date.desc()
            )
            .all()
        )

    @staticmethod
    def get_technicals(
        db: Session,
        instrument_id: int,
        timeframe: str = "1d",
    ):
        from app.models.market_data import (
            TechnicalIndicator,
        )

        return (
            db.query(TechnicalIndicator)
            .filter(
                TechnicalIndicator.instrument_id
                == instrument_id,
                TechnicalIndicator.timeframe
                == timeframe,
            )
            .order_by(
                TechnicalIndicator.calculation_time.desc()
            )
            .first()
        )

    @staticmethod
    def get_news(
        db: Session,
        instrument_id: int,
        limit: int = 20,
    ):
        from app.models.market_data import (
            MarketNews,
        )

        return (
            db.query(MarketNews)
            .filter(
                MarketNews.instrument_id
                == instrument_id
            )
            .order_by(
                MarketNews.published_at.desc()
            )
            .limit(limit)
            .all()
        )