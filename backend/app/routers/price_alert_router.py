from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.utils.auth import get_current_user
from app.services.price_alert_service import PriceAlertService

from app.schemas.price_alert_schema import (
    PriceAlertCreate,
    PriceAlertResponse
)

from app.schemas.common_schema import (
    APIResponse,
    MessageResponse,
    PaginatedData
)


router = APIRouter(
    prefix="/price-alerts",
    tags=["Price Alerts"]
)


# -----------------------------------------
# Create Price Alert
# -----------------------------------------

@router.post(
    "/",
    response_model=APIResponse[PriceAlertResponse],
    status_code=status.HTTP_201_CREATED
)
def create_price_alert(
    alert: PriceAlertCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    created_alert = PriceAlertService.create_alert(
        db,
        current_user.id,
        alert
    )

    return {
        "success": True,
        "message": "Price alert created successfully.",
        "data": created_alert
    }


# -----------------------------------------
# Get User Price Alerts
# -----------------------------------------

@router.get(
    "/",
    response_model=APIResponse[
        PaginatedData[PriceAlertResponse]
    ]
)
def get_price_alerts(
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

    alerts_data = PriceAlertService.get_alerts(
        db=db,
        user_id=current_user.id,
        page=page,
        limit=limit,
        symbol=symbol
    )

    return {
        "success": True,
        "message": "Price alerts fetched successfully.",
        "data": alerts_data
    }


# -----------------------------------------
# Check All Active Price Alerts
# -----------------------------------------

@router.post(
    "/check",
    response_model=APIResponse[dict]
)
def check_price_alerts(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    result = PriceAlertService.check_user_alerts(
        db=db,
        user_id=current_user.id
    )

    return {
        "success": True,
        "message": "Price alerts checked successfully.",
        "data": result
    }


# -----------------------------------------
# Delete Price Alert
# -----------------------------------------

@router.delete(
    "/{alert_id}",
    response_model=MessageResponse
)
def delete_price_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    PriceAlertService.delete_alert(
        db,
        current_user.id,
        alert_id
    )

    return {
        "success": True,
        "message": "Price alert deleted successfully."
    }