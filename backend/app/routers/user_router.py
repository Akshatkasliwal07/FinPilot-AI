from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User

from app.schemas.common_schema import APIResponse
from app.schemas.user_schema import (
    UserCreate,
    UserResponse
)

from app.services.user_service import UserService
from app.utils.auth import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ---------------------------------
# User Signup
# ---------------------------------

@router.post(
    "/signup",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=(
        "Create a new user account by providing "
        "name, email, and password."
    ),
    response_description="Newly created user"
)
def signup(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    created_user = UserService.signup(
        db,
        user
    )

    return {
        "success": True,
        "message": "User registered successfully.",
        "data": created_user
    }


# ---------------------------------
# User Login
# ---------------------------------

@router.post(
    "/login",
    summary="User Login",
    description=(
        "Authenticate a user using email and password, "
        "then return a JWT access token."
    ),
    response_description="JWT access token"
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # Keep access_token and token_type at the top level.
    # Swagger OAuth2 authorization depends on this format.
    return UserService.login(
        db,
        form_data.username,
        form_data.password
    )


# ---------------------------------
# Get Current User
# ---------------------------------

@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Get Current User",
    description=(
        "Retrieve the profile information of the "
        "currently authenticated user."
    ),
    response_description="Current authenticated user"
)
def get_me(
    current_user: User = Depends(get_current_user)
):

    return {
        "success": True,
        "message": "Current user fetched successfully.",
        "data": current_user
    }