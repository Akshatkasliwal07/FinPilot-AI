from fastapi import APIRouter, Query

from app.schemas.common_schema import APIResponse
from app.schemas.news_schema import NewsResponse
from app.services.news_service import NewsService
router = APIRouter(
    prefix="/news",
    tags=["News"]
)


# -----------------------------------------
# General Market News
# -----------------------------------------

@router.get(
    "",
    response_model=APIResponse[NewsResponse],
    summary="Get Market News"
)
def get_market_news(
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Number of market news articles"
    )
):

    news_data = NewsService.get_market_news(
        limit=limit
    )

    return {
        "success": True,
        "message": "Market news fetched successfully.",
        "data": news_data
    }


# -----------------------------------------
# Stock-Specific News
# -----------------------------------------

@router.get(
    "/{symbol}",
    response_model=APIResponse[NewsResponse],
    summary="Get Stock News"
)
def get_stock_news(
    symbol: str,
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Number of news articles to fetch"
    )
):

    news_data = NewsService.get_stock_news(
        symbol=symbol,
        limit=limit
    )

    return {
        "success": True,
        "message": (
            f"News for {symbol.upper()} fetched successfully."
        ),
        "data": news_data
    }