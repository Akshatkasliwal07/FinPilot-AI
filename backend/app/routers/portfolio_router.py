from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.utils.auth import get_current_user
from app.services.portfolio_service import PortfolioService

from app.schemas.portfolio_schema import (
    PortfolioCreate,
    PortfolioResponse,
    PortfolioSummaryResponse
)

from app.schemas.common_schema import (
    APIResponse,
    MessageResponse
)


router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"]
)


@router.post(
    "/",
    response_model=APIResponse[PortfolioResponse],
    status_code=status.HTTP_201_CREATED
)
def add_stock(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    created_portfolio = PortfolioService.add_stock(
        db,
        current_user.id,
        portfolio
    )

    return {
        "success": True,
        "message": "Stock added to portfolio successfully.",
        "data": created_portfolio
    }


@router.get(
    "/summary",
    response_model=APIResponse[PortfolioSummaryResponse]
)
def get_portfolio_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    summary = PortfolioService.get_summary(
        db,
        current_user.id
    )

    return {
        "success": True,
        "message": "Portfolio summary fetched successfully.",
        "data": summary
    }


@router.get(
    "/",
    response_model=APIResponse[list[PortfolioResponse]]
)
def get_my_portfolio(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    portfolio_items = PortfolioService.get_portfolio(
        db,
        current_user.id
    )

    return {
        "success": True,
        "message": "Portfolio fetched successfully.",
        "data": portfolio_items
    }


@router.delete(
    "/{portfolio_id}",
    response_model=MessageResponse
)
def delete_stock(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    PortfolioService.delete_stock(
        db,
        current_user.id,
        portfolio_id
    )

    return {
        "success": True,
        "message": "Portfolio item deleted successfully."
    }