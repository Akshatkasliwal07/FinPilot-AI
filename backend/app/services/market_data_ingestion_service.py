from datetime import datetime

from sqlalchemy.orm import Session

from app.providers.eodhd_provider import (
    EODHDProvider,
)

from app.repositories.market_data_repository import (
    MarketDataRepository,
)


class MarketDataIngestionService:

    # ============================================================
    # IMPORT ONE INSTRUMENT
    # ============================================================

    @staticmethod
    def import_instrument(
        db: Session,
        symbol: str,
        name: str | None = None,
        exchange_code: str | None = None,
        instrument_type: str = "STOCK",
        country: str | None = None,
        currency: str | None = None,
    ):
        exchange_id = None

        if exchange_code:

            exchange = (
                MarketDataRepository.get_exchange(
                    db,
                    exchange_code,
                )
            )

            if not exchange:
                exchange = (
                    MarketDataRepository.create_exchange(
                        db,
                        {
                            "code": exchange_code,
                            "name": exchange_code,
                            "country": country,
                            "currency": currency,
                        },
                    )
                )

            exchange_id = exchange.id

        instrument = (
            MarketDataRepository
            .create_or_update_instrument(
                db,
                {
                    "symbol": symbol.upper(),
                    "name": name or symbol.upper(),
                    "instrument_type": instrument_type,
                    "exchange_id": exchange_id,
                    "country": country,
                    "currency": currency,
                },
            )
        )

        return instrument

    # ============================================================
    # IMPORT LIVE QUOTE
    # ============================================================

    @staticmethod
    def import_quote(
        db: Session,
        symbol: str,
    ):
        symbol = symbol.upper()

        raw = EODHDProvider.get_quote(
            symbol
        )

        if not raw:
            return None

        instrument = (
            MarketDataRepository.get_instrument(
                db,
                symbol,
            )
        )

        if not instrument:
            instrument = (
                MarketDataIngestionService
                .import_instrument(
                    db,
                    symbol,
                )
            )

        quote_time = None

        if raw.get("timestamp"):
            quote_time = datetime.fromtimestamp(
                int(raw["timestamp"])
            )

        quote = (
            MarketDataRepository.upsert_quote(
                db,
                instrument.id,
                {
                    "price":
                        raw.get("close"),

                    "open":
                        raw.get("open"),

                    "high":
                        raw.get("high"),

                    "low":
                        raw.get("low"),

                    "previous_close":
                        raw.get("previousClose"),

                    "change":
                        raw.get("change"),

                    "change_percent":
                        raw.get("change_p"),

                    "volume":
                        raw.get("volume"),

                    "market_cap":
                        raw.get(
                            "marketCapitalization"
                        ),

                    "bid":
                        raw.get("bid"),

                    "ask":
                        raw.get("ask"),

                    "fifty_two_week_high":
                        raw.get("52WeekHigh"),

                    "fifty_two_week_low":
                        raw.get("52WeekLow"),

                    "market_status":
                        raw.get("market_status"),

                    "currency":
                        raw.get("currency"),

                    "data_source":
                        "EODHD",

                    "quote_time":
                        quote_time,
                },
            )
        )

        return quote

    # ============================================================
    # IMPORT HISTORICAL DATA
    # ============================================================

    @staticmethod
    def import_history(
        db: Session,
        symbol: str,
        from_date: str | None = None,
        to_date: str | None = None,
        period: str = "d",
    ):
        symbol = symbol.upper()

        raw = EODHDProvider.get_history(
            symbol,
            from_date,
            to_date,
            period,
        )

        if not raw:
            return 0

        instrument = (
            MarketDataRepository.get_instrument(
                db,
                symbol,
            )
        )

        if not instrument:
            instrument = (
                MarketDataIngestionService
                .import_instrument(
                    db,
                    symbol,
                )
            )

        candles = []

        for row in raw:

            if not row.get("date"):
                continue

            candle_time = datetime.fromisoformat(
                row["date"]
            )

            candles.append(
                {
                    "candle_time":
                        candle_time,

                    "open":
                        row.get("open"),

                    "high":
                        row.get("high"),

                    "low":
                        row.get("low"),

                    "close":
                        row.get("close"),

                    "adjusted_close":
                        row.get(
                            "adjusted_close"
                        ),

                    "volume":
                        row.get("volume"),
                }
            )

        return (
            MarketDataRepository
            .save_price_history(
                db,
                instrument.id,
                candles,
                timeframe="1d",
                data_source="EODHD",
            )
        )

    # ============================================================
    # IMPORT FUNDAMENTALS
    # ============================================================

    @staticmethod
    def import_fundamentals(
        db: Session,
        symbol: str,
    ):
        symbol = symbol.upper()

        raw = EODHDProvider.get_fundamentals(
            symbol
        )

        if not raw:
            return None

        instrument = (
            MarketDataRepository.get_instrument(
                db,
                symbol,
            )
        )

        if not instrument:
            instrument = (
                MarketDataIngestionService
                .import_instrument(
                    db,
                    symbol,
                )
            )

        highlights = raw.get(
            "Highlights",
            {},
        )

        valuation = raw.get(
            "Valuation",
            {},
        )

        data = {
            "market_cap":
                highlights.get(
                    "MarketCapitalization"
                ),

            "revenue":
                highlights.get(
                    "RevenueTTM"
                ),

            "net_income":
                highlights.get(
                    "NetIncomeTTM"
                ),

            "eps":
                highlights.get(
                    "EarningsShare"
                ),

            "dividend_per_share":
                highlights.get(
                    "DividendShare"
                ),

            "dividend_yield":
                highlights.get(
                    "DividendYield"
                ),

            "pe_ratio":
                valuation.get(
                    "TrailingPE"
                ),

            "pb_ratio":
                valuation.get(
                    "PriceBookMRQ"
                ),

            "ps_ratio":
                valuation.get(
                    "PriceSalesTTM"
                ),

            "roe":
                highlights.get(
                    "ReturnOnEquityTTM"
                ),

            "roa":
                highlights.get(
                    "ReturnOnAssetsTTM"
                ),

            "data_source":
                "EODHD",

            "fiscal_year":
                datetime.utcnow().year,

            "fiscal_quarter":
                0,
        }

        return (
            MarketDataRepository
            .save_fundamental(
                db,
                instrument.id,
                data,
            )
        )

    # ============================================================
    # IMPORT COMPLETE STOCK
    # ============================================================

    @staticmethod
    def import_stock(
        db: Session,
        symbol: str,
        from_date: str | None = None,
        to_date: str | None = None,
    ):
        symbol = symbol.upper()

        quote = (
            MarketDataIngestionService
            .import_quote(
                db,
                symbol,
            )
        )

        history_count = (
            MarketDataIngestionService
            .import_history(
                db,
                symbol,
                from_date,
                to_date,
            )
        )

        fundamentals = (
            MarketDataIngestionService
            .import_fundamentals(
                db,
                symbol,
            )
        )

        return {
            "symbol": symbol,

            "quote_imported":
                quote is not None,

            "history_records":
                history_count,

            "fundamentals_imported":
                fundamentals is not None,
        }

    # ============================================================
    # IMPORT EXCHANGE SYMBOL LIST
    # ============================================================

    @staticmethod
    def import_exchange(
        db: Session,
        exchange_code: str,
        country: str | None = None,
        currency: str | None = None,
        batch_size: int = 500,
    ):
        exchange_code = exchange_code.upper()

        # --------------------------------------------------------
        # Get symbols from EODHD
        # --------------------------------------------------------

        symbols = (
            EODHDProvider
            .get_exchange_symbols(
                exchange_code
            )
        )

        if not symbols:
            return {
                "exchange":
                    exchange_code,

                "total":
                    0,

                "imported":
                    0,

                "failed":
                    0,
            }

        # --------------------------------------------------------
        # Get or create exchange
        # --------------------------------------------------------

        exchange = (
            MarketDataRepository
            .get_exchange(
                db,
                exchange_code,
            )
        )

        if not exchange:

            exchange = (
                MarketDataRepository
                .create_exchange(
                    db,
                    {
                        "code":
                            exchange_code,

                        "name":
                            exchange_code,

                        "country":
                            country,

                        "currency":
                            currency,
                    },
                )
            )

        imported = 0
        failed = 0
        batch_counter = 0

        # --------------------------------------------------------
        # Process exchange symbols
        # --------------------------------------------------------

        for item in symbols:

            try:

                symbol = item.get(
                    "Code"
                )

                if not symbol:
                    continue

                symbol = str(
                    symbol
                ).strip().upper()

                name = (
                    item.get("Name")
                    or item.get("Description")
                    or symbol
                )

                instrument_type = (
                    item.get("Type")
                    or "STOCK"
                )

                instrument_type = str(
                    instrument_type
                ).upper()

                # ------------------------------------------------
                # Normalize instrument types
                # ------------------------------------------------

                if instrument_type in {
                    "COMMON STOCK",
                    "STOCK",
                    "EQUITY",
                }:

                    instrument_type = "STOCK"

                elif instrument_type in {
                    "ETF",
                    "ETF FUND",
                }:

                    instrument_type = "ETF"

                elif instrument_type in {
                    "INDEX",
                    "INDICE",
                }:

                    instrument_type = "INDEX"

                elif instrument_type not in {
                    "STOCK",
                    "ETF",
                    "INDEX",
                    "MUTUAL_FUND",
                    "BOND",
                    "CRYPTO",
                    "FOREX",
                    "COMMODITY",
                }:

                    instrument_type = "STOCK"

                # ------------------------------------------------
                # Save instrument
                # ------------------------------------------------

                MarketDataRepository \
                    .create_or_update_instrument(
                        db,
                        {
                            "symbol":
                                symbol,

                            "name":
                                name,

                            "instrument_type":
                                instrument_type,

                            "exchange_id":
                                exchange.id,

                            "isin":
                                item.get(
                                    "Isin"
                                ),

                            "currency":
                                item.get(
                                    "Currency"
                                )
                                or currency,

                            "country":
                                item.get(
                                    "Country"
                                )
                                or country,

                            "sector":
                                item.get(
                                    "Sector"
                                ),

                            "industry":
                                item.get(
                                    "Industry"
                                ),

                            "description":
                                item.get(
                                    "Description"
                                ),
                        },
                        commit=False,
                    )

                imported += 1
                batch_counter += 1

                # ------------------------------------------------
                # Batch commit
                # ------------------------------------------------

                if (
                    batch_counter
                    >= batch_size
                ):

                    db.commit()

                    batch_counter = 0

            except Exception:

                db.rollback()

                failed += 1

                batch_counter = 0

        # --------------------------------------------------------
        # Commit remaining records
        # --------------------------------------------------------

        if batch_counter > 0:
            db.commit()

        return {
            "exchange":
                exchange_code,

            "total":
                len(symbols),

            "imported":
                imported,

            "failed":
                failed,
        }

    # ============================================================
    # IMPORT MULTIPLE EXCHANGES
    # ============================================================

    @staticmethod
    def import_global_exchanges(
        db: Session,
        exchanges: list[dict],
    ):
        results = []

        for exchange in exchanges:

            code = exchange[
                "code"
            ]

            try:

                result = (
                    MarketDataIngestionService
                    .import_exchange(
                        db=db,
                        exchange_code=code,
                        country=exchange.get(
                            "country"
                        ),
                        currency=exchange.get(
                            "currency"
                        ),
                    )
                )

                results.append(
                    {
                        "exchange":
                            code,

                        "success":
                            True,

                        "result":
                            result,
                    }
                )

            except Exception as exc:

                db.rollback()

                results.append(
                    {
                        "exchange":
                            code,

                        "success":
                            False,

                        "error":
                            str(exc),
                    }
                )

        return results
        # ============================================================
    # SYNC ALL SUPPORTED EXCHANGES
    # ============================================================

    @staticmethod
    def sync_exchanges(
        db: Session,
    ):

        exchanges = (
            EODHDProvider.get_exchanges()
        )

        if not exchanges:

            return {
                "total": 0,
                "created": 0,
                "updated": 0,
            }

        created = 0
        updated = 0

        for item in exchanges:

            code = item.get("Code")

            if not code:
                continue

            code = str(code).strip().upper()

            existing = (
                MarketDataRepository.get_exchange(
                    db,
                    code,
                )
            )

            data = {
                "code": code,

                "name":
                    item.get("Name")
                    or code,

                "country":
                    item.get("Country"),

                "country_code":
                    item.get("CountryISO2"),

                "timezone":
                    None,

                "currency":
                    item.get("Currency"),

                "mic":
                    item.get("OperatingMIC"),

                "is_active":
                    True,
            }

            if existing:

                existing.name = data["name"]

                existing.country = data[
                    "country"
                ]

                existing.country_code = data[
                    "country_code"
                ]

                existing.currency = data[
                    "currency"
                ]

                existing.mic = data[
                    "mic"
                ]

                existing.is_active = True

                updated += 1

            else:

                MarketDataRepository.create_exchange(
                    db,
                    data,
                )

                created += 1

        db.commit()

        return {
            "total": len(exchanges),
            "created": created,
            "updated": updated,
        }
        # ============================================================
    # IMPORT INSTRUMENTS FOR AN EXCHANGE
    # ============================================================

    @staticmethod
    def import_exchange_instruments(
        db: Session,
        exchange_code: str,
        batch_size: int = 500,
    ):
        exchange_code = exchange_code.upper()

        # --------------------------------------------------------
        # Find exchange in database
        # --------------------------------------------------------

        exchange = (
            MarketDataRepository.get_exchange(
                db,
                exchange_code,
            )
        )

        if not exchange:
            raise ValueError(
                f"Exchange '{exchange_code}' "
                "does not exist. "
                "Run exchange synchronization first."
            )

        # --------------------------------------------------------
        # Get symbols from EODHD
        # --------------------------------------------------------

        symbols = (
            EODHDProvider
            .get_exchange_symbols(
                exchange_code
            )
        )

        if not symbols:
            return {
                "exchange": exchange_code,
                "total": 0,
                "imported": 0,
                "failed": 0,
            }

        imported = 0
        failed = 0
        batch_counter = 0

        # --------------------------------------------------------
        # Process symbols
        # --------------------------------------------------------

        for item in symbols:

            try:

                symbol = item.get("Code")

                if not symbol:
                    continue

                symbol = str(
                    symbol
                ).strip().upper()

                name = (
                    item.get("Name")
                    or item.get("Description")
                    or symbol
                )

                instrument_type = (
                    item.get("Type")
                    or "STOCK"
                )

                instrument_type = str(
                    instrument_type
                ).strip().upper()

                # ------------------------------------------------
                # Normalize instrument type
                # ------------------------------------------------

                if instrument_type in {
                    "COMMON STOCK",
                    "STOCK",
                    "EQUITY",
                }:
                    instrument_type = "STOCK"

                elif instrument_type in {
                    "ETF",
                    "ETF FUND",
                }:
                    instrument_type = "ETF"

                elif instrument_type in {
                    "INDEX",
                    "INDICE",
                }:
                    instrument_type = "INDEX"

                elif instrument_type in {
                    "MUTUAL FUND",
                    "MUTUAL_FUND",
                }:
                    instrument_type = "MUTUAL_FUND"

                elif instrument_type in {
                    "BOND",
                }:
                    instrument_type = "BOND"

                else:
                    instrument_type = "STOCK"

                # ------------------------------------------------
                # Save instrument
                # ------------------------------------------------

                MarketDataRepository \
                    .create_or_update_instrument(
                        db,
                        {
                            "symbol": symbol,

                            "name": name,

                            "instrument_type":
                                instrument_type,

                            "exchange_id":
                                exchange.id,

                            "isin":
                                item.get("Isin"),

                            "currency":
                                item.get(
                                    "Currency"
                                ),

                            "country":
                                item.get(
                                    "Country"
                                ),

                            "sector":
                                item.get(
                                    "Sector"
                                ),

                            "industry":
                                item.get(
                                    "Industry"
                                ),

                            "description":
                                item.get(
                                    "Description"
                                ),
                        },

                        commit=False,
                    )

                imported += 1
                batch_counter += 1

                # ------------------------------------------------
                # Batch commit
                # ------------------------------------------------

                if batch_counter >= batch_size:

                    db.commit()

                    batch_counter = 0

            except Exception:

                db.rollback()

                failed += 1

                batch_counter = 0

        # --------------------------------------------------------
        # Remaining records
        # --------------------------------------------------------

        if batch_counter > 0:
            db.commit()

        return {
            "exchange": exchange_code,
            "total": len(symbols),
            "imported": imported,
            "failed": failed,
        }