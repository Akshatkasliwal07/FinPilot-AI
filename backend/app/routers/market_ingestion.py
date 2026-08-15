from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.services.market_data_service import (
    MarketDataService,
)

from app.services.market_data_ingestion_service import (
    MarketDataIngestionService,
)


router = APIRouter(
    prefix="/api/market/ingestion",
    tags=["Market Data Ingestion"],
)


# ============================================================
# INDIA ONLY
# ============================================================

INDIAN_EXCHANGES = {
    "NSE",
    "BSE",
}


# ============================================================
# IMPORT COMPLETE STOCK
# ============================================================

@router.post("/stock/{symbol}")
def import_stock(
    symbol: str,
    from_date: str | None = Query(
        default=None,
        description="YYYY-MM-DD",
    ),
    to_date: str | None = Query(
        default=None,
        description="YYYY-MM-DD",
    ),
    db: Session = Depends(get_db),
):
    symbol = symbol.strip().upper()

    try:

        result = (
            MarketDataIngestionService
            .import_stock(
                db=db,
                symbol=symbol,
                from_date=from_date,
                to_date=to_date,
            )
        )

        return {
            "success": True,
            "message": (
                f"{symbol} market data "
                "imported successfully."
            ),
            "data": result,
        }

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# IMPORT LIVE QUOTE
# ============================================================

@router.post("/quote/{symbol}")
def import_quote(
    symbol: str,
    db: Session = Depends(get_db),
):
    symbol = symbol.strip().upper()

    try:

        quote = (
            MarketDataIngestionService
            .import_quote(
                db=db,
                symbol=symbol,
            )
        )

        if not quote:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"No quote data found "
                    f"for {symbol}."
                ),
            )

        return {
            "success": True,
            "message": (
                f"Quote for {symbol} "
                "imported successfully."
            ),
            "data": {
                "id": quote.id,
                "instrument_id": quote.instrument_id,
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
                "quote_time": quote.quote_time,
            },
        }

    except HTTPException:
        raise

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# IMPORT HISTORICAL DATA
# ============================================================

@router.post("/history/{symbol}")
def import_history(
    symbol: str,
    from_date: str | None = Query(
        default=None,
        description="YYYY-MM-DD",
    ),
    to_date: str | None = Query(
        default=None,
        description="YYYY-MM-DD",
    ),
    db: Session = Depends(get_db),
):
    symbol = symbol.strip().upper()

    try:

        count = (
            MarketDataIngestionService
            .import_history(
                db=db,
                symbol=symbol,
                from_date=from_date,
                to_date=to_date,
            )
        )

        return {
            "success": True,
            "message": (
                f"Historical data for "
                f"{symbol} imported."
            ),
            "data": {
                "symbol": symbol,
                "records_imported": count,
            },
        }

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# IMPORT FUNDAMENTALS
# ============================================================

@router.post("/fundamentals/{symbol}")
def import_fundamentals(
    symbol: str,
    db: Session = Depends(get_db),
):
    symbol = symbol.strip().upper()

    try:

        result = (
            MarketDataIngestionService
            .import_fundamentals(
                db=db,
                symbol=symbol,
            )
        )

        if not result:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"No fundamental data found "
                    f"for {symbol}."
                ),
            )

        return {
            "success": True,
            "message": (
                f"Fundamentals for "
                f"{symbol} imported."
            ),
            "data": {
                "symbol": symbol,
                "imported": True,
            },
        }

    except HTTPException:
        raise

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# IMPORT NSE / BSE EXCHANGE
# ============================================================

@router.post("/exchange/{exchange_code}")
def import_exchange(
    exchange_code: str,
    country: str | None = Query(
        default="India",
    ),
    currency: str | None = Query(
        default="INR",
    ),
    db: Session = Depends(get_db),
):
    exchange_code = (
        exchange_code.strip().upper()
    )

    if exchange_code not in INDIAN_EXCHANGES:

        raise HTTPException(
            status_code=400,
            detail=(
                "FinPilot supports only "
                "Indian exchanges: NSE and BSE."
            ),
        )

    try:

        result = (
            MarketDataIngestionService
            .import_exchange(
                db=db,
                exchange_code=exchange_code,
                country="India",
                currency="INR",
            )
        )

        return {
            "success": True,
            "message": (
                f"Indian exchange "
                f"{exchange_code} imported successfully."
            ),
            "data": result,
        }

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# SYNC INDIAN EXCHANGES
# ============================================================

@router.post("/exchanges/sync")
def sync_exchanges(
    db: Session = Depends(get_db),
):
    try:

        results = []

        for exchange_code in (
            "NSE",
            "BSE",
        ):

            result = (
                MarketDataIngestionService
                .import_exchange(
                    db=db,
                    exchange_code=exchange_code,
                    country="India",
                    currency="INR",
                )
            )

            results.append(
                {
                    "exchange": exchange_code,
                    "result": result,
                }
            )

        return {
            "success": True,
            "message": (
                "NSE and BSE synchronized successfully."
            ),
            "data": results,
        }

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# IMPORT NSE / BSE STOCK UNIVERSE
# ============================================================

@router.post(
    "/exchange/{exchange_code}/instruments"
)
def import_exchange_instruments(
    exchange_code: str,
    batch_size: int = 1000,
    db: Session = Depends(get_db),
):
    exchange_code = (
        exchange_code.strip().upper()
    )

    # --------------------------------------------------------
    # India only
    # --------------------------------------------------------

    if exchange_code not in INDIAN_EXCHANGES:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only NSE and BSE are supported."
            ),
        )

    # --------------------------------------------------------
    # Batch size
    # --------------------------------------------------------

    if batch_size < 50:
        batch_size = 50

    if batch_size > 2000:
        batch_size = 2000

    try:

        result = (
            MarketDataService
            .import_exchange_instruments(
                db=db,
                exchange_code=exchange_code,
                batch_size=batch_size,
            )
        )

        return {
            "success": True,
            "message": (
                f"{exchange_code} Indian stocks "
                "imported successfully."
            ),
            "data": result,
        }

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )