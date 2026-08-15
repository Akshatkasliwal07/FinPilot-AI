from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from app.core.exceptions import FinPilotException

from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
)


class UserService:

    @staticmethod
    def signup(db: Session, user: UserCreate):

        existing_user = UserRepository.get_user_by_email(
            db,
            user.email
        )

        if existing_user:
            raise FinPilotException(
                "Email already registered",
                400
            )

        new_user = User(
            name=user.name,
            email=user.email,
            hashed_password=hash_password(user.password)
        )

        return UserRepository.create_user(
            db,
            new_user
        )


    @staticmethod
    def login(
        db: Session,
        email: str,
        password: str
    ):

        user = UserRepository.get_user_by_email(
            db,
            email
        )

        if not user:
            raise FinPilotException(
                "Invalid email or password",
                401
            )

        if not verify_password(
            password,
            user.hashed_password
        ):
            raise FinPilotException(
                "Invalid email or password",
                401
            )


        access_token = create_access_token(
            data={
                "sub": user.email
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }