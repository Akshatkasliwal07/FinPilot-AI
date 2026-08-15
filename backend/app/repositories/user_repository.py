from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.user import User


class UserRepository:

    @staticmethod
    def create_user(
        db: Session,
        user: User
    ):
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user

        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def get_user_by_email(
        db: Session,
        email: str
    ):
        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

    @staticmethod
    def get_user_by_id(
        db: Session,
        user_id: int
    ):
        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )