from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    hashed_password = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # One user can have many portfolio entries
    portfolio = relationship(
        "Portfolio",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # One user can have many watchlist entries
    watchlist = relationship(
        "Watchlist",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # One user can have many price alerts
    price_alerts = relationship(
        "PriceAlert",
        back_populates="user",
        cascade="all, delete-orphan"
    )