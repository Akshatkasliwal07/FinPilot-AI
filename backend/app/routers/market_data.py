from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import yfinance as yf

from app.database.database import get_db
from app.services.market_data_service import MarketDataService


router = APIRouter(
    prefix="/api/market",
    tags=["Market Data"],
)


# ============================================================
# HELPERS
# ============================================================

def normalize_symbol(symbol: str) -> str:
    """
    Convert a user-facing Indian stock symbol into a
    Yahoo Finance symbol.

    Examples:
        TCS      -> TCS.NS
        IRCTC    -> IRCTC.NS
        RELIANCE -> RELIANCE.NS

    If the user already supplies .NS / .BO or an index
    symbol, it is kept as-is.
    """

    symbol = symbol.strip().upper()

    if not symbol:
        raise HTTPException(
            status_code=400,
            detail="Stock symbol is required.",
        )

    # Yahoo index symbols
    if symbol.startswith("^"):
        return symbol

    # Already a Yahoo symbol
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        return symbol

    # Known non-equity symbols that should not receive .NS
    special_symbols = {
        "NIFTY",
        "NIFTY50",
        "NIFTY 50",
        "SENSEX",
        "BANKNIFTY",
    }

    if symbol in special_symbols:
        return symbol

    return f"{symbol}.NS"


def safe_float(value):
    """
    Safely convert Yahoo Finance values to float.
    """
    try:
        if value is None:
            return None

        # Handle NaN
        numeric = float(value)

        if numeric != numeric:
            return None

        return numeric

    except (TypeError, ValueError):
        return None


def normalize_timestamp(timestamp):
    """
    Convert pandas/Yahoo timestamps into ISO strings.
    """
    try:
        if hasattr(timestamp, "isoformat"):
            return timestamp.isoformat()

        return str(timestamp)

    except Exception:
        return str(timestamp)


# ============================================================
# SEARCH
# ============================================================

@router.get("/search")
def search_market(
    q: str = Query(
        "",
        min_length=0,
        max_length=100,
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    query = q.strip().upper()

    result = MarketDataService.search(
        db=db,
        query=query,
        limit=limit,
    )

    # India-only safety filter
    result = [
        item
        for item in result
        if (
            str(
                item.get("currency", "")
            ).upper()
            == "INR"
            or
            str(
                item.get("country", "")
            ).upper()
            == "INDIA"
        )
    ]

    return {
        "success": True,
        "data": result,
    }


# ============================================================
# DATABASE QUOTE
# ============================================================

@router.get("/quote/{symbol}")
def get_quote(
    symbol: str,
    db: Session = Depends(get_db),
):
    symbol = symbol.strip().upper()

    result = MarketDataService.get_quote(
        db=db,
        symbol=symbol,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"{symbol} not found",
        )

    return {
        "success": True,
        "data": result,
    }


# ============================================================
# HISTORY
# ============================================================

@router.get("/history/{symbol}")
def get_history(
    symbol: str,
    timeframe: str = "1d",
    limit: int = Query(
        365,
        ge=1,
        le=5000,
    ),
    db: Session = Depends(get_db),
):
    symbol = symbol.strip().upper()

    result = MarketDataService.get_history(
        db=db,
        symbol=symbol,
        timeframe=timeframe,
        limit=limit,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"{symbol} not found",
        )

    return {
        "success": True,
        "data": result,
    }


# ============================================================
# FUNDAMENTALS
# ============================================================

@router.get("/fundamentals/{symbol}")
def get_fundamentals(
    symbol: str,
    db: Session = Depends(get_db),
):
    symbol = symbol.strip().upper()

    result = MarketDataService.get_fundamentals(
        db=db,
        symbol=symbol,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"{symbol} not found",
        )

    return {
        "success": True,
        "data": result,
    }


# ============================================================
# TECHNICALS
# ============================================================

@router.get("/technicals/{symbol}")
def get_technicals(
    symbol: str,
    timeframe: str = "1d",
    db: Session = Depends(get_db),
):
    symbol = symbol.strip().upper()

    result = MarketDataService.get_technicals(
        db=db,
        symbol=symbol,
        timeframe=timeframe,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No technical data for {symbol}",
        )

    return {
        "success": True,
        "data": result,
    }


# ============================================================
# NEWS
# ============================================================

@router.get("/news/{symbol}")
def get_news(
    symbol: str,
    limit: int = Query(
        20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    symbol = symbol.strip().upper()

    result = MarketDataService.get_news(
        db=db,
        symbol=symbol,
        limit=limit,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"{symbol} not found",
        )

    return {
        "success": True,
        "data": result,
    }


# ============================================================
# LIVE PROVIDER QUOTE
# ============================================================

@router.get("/live/quote/{symbol}")
def live_quote(
    symbol: str,
):
    symbol = symbol.strip().upper()

    try:

        # ----------------------------------------------------
        # STEP 1
        # Try EODHD live quote
        # ----------------------------------------------------

        live = MarketDataService.provider_quote(
            symbol
        )

        if not isinstance(live, dict):
            live = {}

        # ----------------------------------------------------
        # Safe number conversion
        # ----------------------------------------------------

        def number_or_none(value):

            if value is None:
                return None

            if str(value).strip().upper() in (
                "",
                "NA",
                "N/A",
                "NULL",
                "NONE",
            ):
                return None

            try:
                return float(value)

            except (
                TypeError,
                ValueError,
            ):
                return None

        # ----------------------------------------------------
        # Live values
        # ----------------------------------------------------

        price = number_or_none(
            live.get("close")
        )

        open_price = number_or_none(
            live.get("open")
        )

        high = number_or_none(
            live.get("high")
        )

        low = number_or_none(
            live.get("low")
        )

        previous_close = number_or_none(
            live.get("previousClose")
        )

        change = number_or_none(
            live.get("change")
        )

        change_percent = number_or_none(
            live.get("change_p")
        )

        volume = number_or_none(
            live.get("volume")
        )

        # ====================================================
        # STEP 2
        # Fallback to latest EOD history
        # ====================================================

        if price is None:

            history = (
                MarketDataService
                .provider_history(
                    symbol=symbol,
                    period="d",
                )
            )

            if (
                isinstance(history, list)
                and len(history) > 0
            ):

                # Provider history is ordered ascending
                latest = history[-1]

                if isinstance(
                    latest,
                    dict,
                ):

                    price = number_or_none(
                        latest.get("close")
                    )

                    open_price = (
                        open_price
                        if open_price is not None
                        else number_or_none(
                            latest.get("open")
                        )
                    )

                    high = (
                        high
                        if high is not None
                        else number_or_none(
                            latest.get("high")
                        )
                    )

                    low = (
                        low
                        if low is not None
                        else number_or_none(
                            latest.get("low")
                        )
                    )

                    volume = (
                        volume
                        if volume is not None
                        else number_or_none(
                            latest.get("volume")
                        )
                    )

                    # ------------------------------------------------
                    # Previous candle
                    # ------------------------------------------------

                    if (
                        previous_close is None
                        and len(history) >= 2
                    ):

                        previous = history[-2]

                        if isinstance(
                            previous,
                            dict,
                        ):

                            previous_close = (
                                number_or_none(
                                    previous.get(
                                        "close"
                                    )
                                )
                            )

        # ====================================================
        # STEP 3
        # Calculate change if necessary
        # ====================================================

        if (
            price is not None
            and previous_close is not None
        ):

            if change is None:

                change = (
                    price
                    - previous_close
                )

            if (
                change_percent is None
                and previous_close != 0
            ):

                change_percent = (
                    (
                        price
                        - previous_close
                    )
                    / previous_close
                ) * 100

        # ====================================================
        # STEP 4
        # Determine status
        # ====================================================

        live_timestamp = live.get(
            "timestamp"
        )

        if (
            price is not None
            and live_timestamp
            and str(
                live_timestamp
            ).upper()
            not in (
                "NA",
                "N/A",
                "NONE",
                "NULL",
            )
        ):

            market_status = "live"

        elif price is not None:

            market_status = (
                "latest_available"
            )

        else:

            market_status = (
                "unavailable"
            )

        # ====================================================
        # STEP 5
        # Return normalized response
        # ====================================================

        return {
            "success": True,

            "data": {

                "symbol": symbol,

                "code": live.get(
                    "code",
                    f"{symbol}.XNSE",
                ),

                "price": price,

                "open": open_price,

                "high": high,

                "low": low,

                "previous_close":
                    previous_close,

                "change": change,

                "change_percent":
                    change_percent,

                "volume": volume,

                "timestamp":
                    live_timestamp,

                "market_status":
                    market_status,

                "data_source":
                    "EODHD",
            },
        }

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# LIVE PROVIDER HISTORY
# ============================================================

@router.get("/live/history/{symbol}")
def live_history(
    symbol: str,
    from_date: str | None = None,
    to_date: str | None = None,
    period: str = "1mo",
):
    """
    Historical market data used by the Stock Details chart.

    IMPORTANT:
    5D is intentionally mapped to Yahoo Finance 5-minute
    intraday candles so the frontend receives real timestamps.

    Other periods continue using the existing provider history.
    """

    symbol = symbol.strip().upper()
    period = period.strip().lower()

    try:

        # ========================================================
        # 5D = TRUE INTRADAY CANDLES
        # ========================================================

        if period == "5d":

            yahoo_symbol = normalize_symbol(symbol)

            ticker = yf.Ticker(
                yahoo_symbol
            )

            history = ticker.history(
                period="5d",
                interval="5m",
                auto_adjust=False,
                prepost=False,
            )

            if (
                history is None
                or history.empty
            ):
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"No 5-day intraday data "
                        f"available for {symbol}."
                    ),
                )

            candles = []

            for timestamp, row in history.iterrows():

                open_value = safe_float(
                    row.get("Open")
                )

                high_value = safe_float(
                    row.get("High")
                )

                low_value = safe_float(
                    row.get("Low")
                )

                close_value = safe_float(
                    row.get("Close")
                )

                volume_value = safe_float(
                    row.get("Volume")
                )

                # Skip invalid candles
                if (
                    open_value is None
                    or high_value is None
                    or low_value is None
                    or close_value is None
                ):
                    continue

                timestamp_string = (
                    normalize_timestamp(
                        timestamp
                    )
                )

                candles.append(
                    {
                        "date":
                            timestamp_string,

                        "timestamp":
                            timestamp_string,

                        "datetime":
                            timestamp_string,

                        "open":
                            round(
                                open_value,
                                4,
                            ),

                        "high":
                            round(
                                high_value,
                                4,
                            ),

                        "low":
                            round(
                                low_value,
                                4,
                            ),

                        "close":
                            round(
                                close_value,
                                4,
                            ),

                        "volume":
                            int(
                                volume_value
                            )
                            if volume_value
                            is not None
                            else 0,
                    }
                )

            if not candles:

                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"No valid intraday candles "
                        f"found for {symbol}."
                    ),
                )

            return {
                "success": True,

                "data": candles,
            }

        # ========================================================
        # OTHER PERIODS = EXISTING PROVIDER HISTORY
        # ========================================================

        result = (
            MarketDataService
            .provider_history(
                symbol,
                from_date,
                to_date,
                period,
            )
        )

        return {
            "success": True,
            "data": result,
        }

    except HTTPException:
        raise

    except Exception as exc:

        print(
            f"Live history error for "
            f"{symbol}: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to fetch history "
                f"for {symbol}: {str(exc)}"
            ),
        )


# ============================================================
# TRUE INTRADAY OHLC CANDLES
# ============================================================

@router.get("/live/intraday/{symbol}")
def live_intraday(
    symbol: str,

    interval: str = Query(
        "5m",
        description=(
            "Yahoo Finance interval: "
            "1m, 2m, 5m, 15m, 30m, 60m, 1d"
        ),
    ),

    period: str = Query(
        "5d",
        description=(
            "Yahoo Finance period: "
            "1d, 5d, 1mo, 3mo, 6mo, 1y"
        ),
    ),
):
    """
    Return real OHLCV intraday candles from Yahoo Finance.

    Examples:

        /api/market/live/intraday/TCS?interval=5m&period=5d

        /api/market/live/intraday/IRCTC?interval=15m&period=5d

        /api/market/live/intraday/RELIANCE?interval=1h&period=1mo
    """

    symbol = symbol.strip().upper()
    interval = interval.strip().lower()
    period = period.strip().lower()

    # --------------------------------------------------------
    # Allowed intervals
    # --------------------------------------------------------

    allowed_intervals = {
        "1m",
        "2m",
        "5m",
        "15m",
        "30m",
        "60m",
        "1d",
    }

    if interval not in allowed_intervals:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid interval. Use one of: "
                "1m, 2m, 5m, 15m, 30m, 60m, 1d."
            ),
        )

    # --------------------------------------------------------
    # Allowed periods
    # --------------------------------------------------------

    allowed_periods = {
        "1d",
        "5d",
        "1mo",
        "3mo",
        "6mo",
        "1y",
    }

    if period not in allowed_periods:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid period. Use one of: "
                "1d, 5d, 1mo, 3mo, 6mo, 1y."
            ),
        )

    # --------------------------------------------------------
    # Yahoo limitations for 1m candles
    # --------------------------------------------------------

    if interval == "1m" and period not in {
        "1d",
        "5d",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "Yahoo Finance provides 1-minute candles "
                "only for a limited recent period. "
                "Use period=1d or period=5d for 1m candles."
            ),
        )

    # --------------------------------------------------------
    # Yahoo limitations for 2m candles
    # --------------------------------------------------------

    if interval == "2m" and period in {
        "6mo",
        "1y",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "2-minute candles are not available for "
                "long historical periods. Use 1d, 5d, "
                "1mo or 3mo."
            ),
        )

    # --------------------------------------------------------
    # Yahoo symbol
    # --------------------------------------------------------

    yahoo_symbol = normalize_symbol(symbol)

    try:

        ticker = yf.Ticker(
            yahoo_symbol
        )

        # ----------------------------------------------------
        # Download OHLCV data
        # ----------------------------------------------------

        history = ticker.history(
            period=period,
            interval=interval,
            auto_adjust=False,
            prepost=False,
        )

        if history is None or history.empty:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"No intraday market data "
                    f"available for {symbol}."
                ),
            )

        candles = []

        # ----------------------------------------------------
        # Convert pandas rows into JSON-safe candles
        # ----------------------------------------------------

        for timestamp, row in history.iterrows():

            open_value = safe_float(
                row.get("Open")
            )

            high_value = safe_float(
                row.get("High")
            )

            low_value = safe_float(
                row.get("Low")
            )

            close_value = safe_float(
                row.get("Close")
            )

            volume_value = safe_float(
                row.get("Volume")
            )

            # Ignore incomplete/invalid rows
            if (
                open_value is None
                or high_value is None
                or low_value is None
                or close_value is None
            ):
                continue

            candles.append(
                {
                    "timestamp":
                        normalize_timestamp(
                            timestamp
                        ),

                    "date":
                        normalize_timestamp(
                            timestamp
                        ),

                    "open":
                        round(
                            open_value,
                            4,
                        ),

                    "high":
                        round(
                            high_value,
                            4,
                        ),

                    "low":
                        round(
                            low_value,
                            4,
                        ),

                    "close":
                        round(
                            close_value,
                            4,
                        ),

                    "volume":
                        int(volume_value)
                        if volume_value is not None
                        else 0,
                }
            )

        if not candles:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"No valid candles found "
                    f"for {symbol}."
                ),
            )

        # ----------------------------------------------------
        # Return latest candle information
        # ----------------------------------------------------

        latest = candles[-1]

        return {
            "success": True,

            "data": {
                "symbol": symbol,

                "yahoo_symbol":
                    yahoo_symbol,

                "interval":
                    interval,

                "period":
                    period,

                "count":
                    len(candles),

                "latest":
                    latest,

                "candles":
                    candles,

                "data_source":
                    "Yahoo Finance",

                "market_status":
                    "available",
            },
        }

    except HTTPException:
        raise

    except Exception as exc:

        print(
            f"Intraday data error for "
            f"{symbol}: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to fetch intraday "
                f"data for {symbol}: {str(exc)}"
            ),
        )


# ============================================================
# LIVE PROVIDER NEWS
# ============================================================

@router.get("/live/news")
def live_news(
    symbol: str | None = None,
    limit: int = Query(
        20,
        ge=1,
        le=100,
    ),
):
    try:

        result = (
            MarketDataService
            .provider_news(
                symbol=(
                    symbol.strip().upper()
                    if symbol
                    else None
                ),
                limit=limit,
            )
        )

        return {
            "success": True,
            "data": result,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# LIVE INDIAN MARKET INDICES
# NIFTY 50 + SENSEX
# ============================================================

@router.get("/live/indices")
def live_indian_indices():

    indices = {
        "NIFTY 50": "^NSEI",
        "SENSEX": "^BSESN",
    }

    result = {}

    for name, yahoo_symbol in indices.items():

        try:

            ticker = yf.Ticker(
                yahoo_symbol
            )

            history = ticker.history(
                period="5d",
                interval="1d",
            )

            if history.empty:

                result[name] = {
                    "symbol":
                        yahoo_symbol,

                    "price":
                        None,

                    "previous_close":
                        None,

                    "change":
                        None,

                    "change_percent":
                        None,

                    "timestamp":
                        None,

                    "market_status":
                        "unavailable",

                    "data_source":
                        "Yahoo Finance",
                }

                continue

            latest = history.iloc[-1]

            price = float(
                latest["Close"]
            )

            previous_close = None

            if len(history) >= 2:

                previous_close = float(
                    history["Close"].iloc[-2]
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

            result[name] = {

                "symbol":
                    yahoo_symbol,

                "price":
                    round(
                        price,
                        2,
                    ),

                "previous_close": (
                    round(
                        previous_close,
                        2,
                    )
                    if previous_close is not None
                    else None
                ),

                "change":
                    round(
                        change,
                        2,
                    ),

                "change_percent":
                    round(
                        change_percent,
                        2,
                    ),

                "timestamp":
                    str(
                        history.index[-1].date()
                    ),

                "market_status":
                    "available",

                "data_source":
                    "Yahoo Finance",
            }

        except Exception as exc:

            print(
                f"Index data error for "
                f"{name}: {exc}"
            )

            result[name] = {

                "symbol":
                    yahoo_symbol,

                "price":
                    None,

                "previous_close":
                    None,

                "change":
                    None,

                "change_percent":
                    None,

                "timestamp":
                    None,

                "market_status":
                    "error",

                "data_source":
                    "Yahoo Finance",
            }

    return {
        "success": True,
        "data": result,
    }