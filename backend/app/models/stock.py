from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database.database import Base


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)

    symbol = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    company_name = Column(
        String(255),
        nullable=False
    )

    exchange = Column(
        String(50),
        nullable=False
    )

    sector = Column(
        String(100),
        nullable=True
    )

    industry = Column(
        String(100),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )