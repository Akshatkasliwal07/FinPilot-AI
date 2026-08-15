from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    stock_id = Column(
        Integer,
        ForeignKey(
            "stocks.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # User relationship
    user = relationship(
        "User",
        back_populates="watchlist"
    )

    # Stock relationship
    stock = relationship(
        "Stock"
    )

    # A user cannot add the same stock twice
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "stock_id",
            name="uq_user_stock_watchlist"
        ),
    )