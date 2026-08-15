from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Boolean,
    ForeignKey,
    DateTime
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class PriceAlert(Base):

    __tablename__ = "price_alerts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    stock_symbol = Column(
        String(20),
        nullable=False
    )

    target_price = Column(
        Float,
        nullable=False
    )

    condition = Column(
        String(10),
        nullable=False
    )

    is_triggered = Column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user = relationship(
        "User",
        back_populates="price_alerts"
    )