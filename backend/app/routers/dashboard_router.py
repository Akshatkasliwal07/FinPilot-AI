from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.common_schema import APIResponse
from app.schemas.dashboard_schema import DashboardData
from app.services.dashboard_service import DashboardService
from app.utils.auth import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "",
    response_model=APIResponse[DashboardData],
    summary="Get User Dashboard"
)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    dashboard_data = DashboardService.get_dashboard(
        db,
        current_user
    )

    return {
        "success": True,
        "message": "Dashboard fetched successfully.",
        "data": dashboard_data
    }