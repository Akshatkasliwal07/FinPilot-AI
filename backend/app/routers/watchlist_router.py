from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.utils.auth import get_current_user
from app.services.watchlist_service import WatchlistService

from app.schemas.watchlist_schema import (
    WatchlistCreate,
    WatchlistResponse
)

from app.schemas.common_schema import (
    APIResponse,
    MessageResponse,
    PaginatedData
)


router = APIRouter(
    prefix="/watchlist",
    tags=["Watchlist"]
)


@router.post(
    "/",
    response_model=APIResponse[WatchlistResponse],
    status_code=status.HTTP_201_CREATED
)
def add_stock_to_watchlist(
    watchlist: WatchlistCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    created_item = WatchlistService.add_stock(
        db,
        current_user.id,
        watchlist
    )

    return {
        "success": True,
        "message": "Stock added to watchlist successfully.",
        "data": created_item
    }


@router.get(
    "/",
    response_model=APIResponse[
        PaginatedData[WatchlistResponse]
    ]
)
def get_my_watchlist(
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
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    watchlist_data = WatchlistService.get_watchlist(
        db=db,
        user_id=current_user.id,
        page=page,
        limit=limit,
        symbol=symbol
    )

    return {
        "success": True,
        "message": "Watchlist fetched successfully.",
        "data": watchlist_data
    }


@router.delete(
    "/{watchlist_id}",
    response_model=MessageResponse
)
def delete_watchlist_item(
    watchlist_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    WatchlistService.delete_stock(
        db,
        current_user.id,
        watchlist_id
    )

    return {
        "success": True,
        "message": "Watchlist item deleted successfully."
    }