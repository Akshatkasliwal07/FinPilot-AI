from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.exceptions import FinPilotException
from app.schemas.common_schema import (
    APIResponse,
    PaginatedData
)
from app.schemas.stock_schema import (
    StockCreate,
    StockResponse
)
from app.services.stock_service import StockService
from app.services.technical_analysis_service import (
    TechnicalAnalysisService,
)

router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"]
)


# ---------------------------------
# Create Stock
# ---------------------------------

@router.post(
    "",
    response_model=APIResponse[StockResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Stock"
)
def create_stock(
    stock: StockCreate,
    db: Session = Depends(get_db)
):

    created_stock = StockService.create_stock(
        db,
        stock
    )

    return {
        "success": True,
        "message": "Stock created successfully.",
        "data": created_stock
    }


# ---------------------------------
# Get Stocks with Pagination
# ---------------------------------

@router.get(
    "",
    response_model=APIResponse[
        PaginatedData[StockResponse]
    ],
    summary="Get Stocks"
)
def get_all_stocks(
    page: int = Query(
        default=1,
        ge=1
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),
    symbol: str | None = Query(
        default=None
    ),
    sector: str | None = Query(
        default=None
    ),
    db: Session = Depends(get_db)
):

    stocks_data = StockService.get_all_stocks(
        db=db,
        page=page,
        limit=limit,
        symbol=symbol,
        sector=sector
    )

    return {
        "success": True,
        "message": "Stocks fetched successfully.",
        "data": stocks_data
    }


# ---------------------------------
# Get Live Stock Data
# ---------------------------------

@router.get(
    "/live/{symbol}",
    response_model=APIResponse[dict],
    summary="Get Live Stock Data"
)
def get_live_stock(
    symbol: str
):

    stock_data = StockService.get_live_stock(
        symbol
    )

    return {
        "success": True,
        "message": (
            f"Live stock data for "
            f"{symbol.upper()} fetched successfully."
        ),
        "data": stock_data
    }
# ---------------------------------
# Get Historical Stock Data
# ---------------------------------

@router.get(
    "/history/{symbol}",
    response_model=APIResponse[dict],
    summary="Get Historical Stock Data"
)
def get_stock_history(
    symbol: str,
    period: str = Query(
        default="1mo"
    )
):

    history = StockService.get_stock_history(
        symbol,
        period
    )

    return {
        "success": True,
        "message": (
            f"Historical stock data for "
            f"{symbol.upper()} fetched successfully."
        ),
        "data": history
    }
# ---------------------------------
# Get Technical Analysis
# ---------------------------------

@router.get(
    "/analysis/{symbol}",
    response_model=APIResponse[dict],
    summary="Get Technical Analysis",
)
def get_technical_analysis(
    symbol: str,
    period: str = Query(
        default="3mo",
    ),
):
    try:
        history_data = StockService.get_stock_history(
            symbol=symbol,
            period=period,
        )

        history = history_data["items"]

        analysis = (
            TechnicalAnalysisService
            .calculate_indicators(history)
        )

        if not analysis["success"]:
            raise FinPilotException(
                analysis["message"],
                500,
            )

        return {
            "success": True,
            "message": (
                f"Technical analysis for "
                f"{symbol.upper()} calculated successfully."
            ),
            "data": analysis["data"],
        }

    except FinPilotException:
        raise

    except Exception as exc:
        print(
            f"Technical analysis error for {symbol}:",
            exc,
        )

        raise FinPilotException(
            "Unable to calculate technical analysis.",
            500,
        )