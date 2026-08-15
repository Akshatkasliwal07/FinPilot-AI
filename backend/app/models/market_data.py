from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


# ============================================================
# EXCHANGE
# ============================================================

class Exchange(Base):
    __tablename__ = "exchanges"

    id = Column(
        BigInteger,
        primary_key=True,
    )

    code = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
    )

    name = Column(
        String(150),
        nullable=False,
    )

    country = Column(
        String(100),
    )

    country_code = Column(
        String(10),
    )

    timezone = Column(
        String(100),
    )

    currency = Column(
        String(20),
    )

    mic = Column(
        String(20),
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    instruments = relationship(
        "MarketInstrument",
        back_populates="exchange",
        cascade="all, delete-orphan",
    )


# ============================================================
# MARKET INSTRUMENT
# ============================================================

class MarketInstrument(Base):
    __tablename__ = "market_instruments"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
    )

    symbol = Column(
        String(50),
        nullable=False,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
    )

    instrument_type = Column(
        String(50),
        nullable=False,
        default="STOCK",
    )

    exchange_id = Column(
        BigInteger,
        ForeignKey(
            "exchanges.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    isin = Column(
        String(50),
        nullable=True,
        index=True,
    )

    cusip = Column(
        String(50),
        nullable=True,
    )

    currency = Column(
        String(20),
        nullable=True,
    )

    country = Column(
        String(100),
        nullable=True,
    )

    sector = Column(
        String(100),
        nullable=True,
    )

    industry = Column(
        String(150),
        nullable=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    website = Column(
        String(500),
        nullable=True,
    )

    logo_url = Column(
        String(500),
        nullable=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    exchange = relationship(
        "Exchange",
        back_populates="instruments",
    )

    quote = relationship(
        "MarketQuote",
        back_populates="instrument",
        uselist=False,
        cascade="all, delete-orphan",
    )

    price_history = relationship(
        "PriceHistory",
        back_populates="instrument",
        cascade="all, delete-orphan",
    )

    fundamentals = relationship(
        "Fundamental",
        back_populates="instrument",
        cascade="all, delete-orphan",
    )

    technical_indicators = relationship(
        "TechnicalIndicator",
        back_populates="instrument",
        cascade="all, delete-orphan",
    )

    news = relationship(
        "MarketNews",
        back_populates="instrument",
    )

    market_index = relationship(
        "MarketIndex",
        back_populates="instrument",
        uselist=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "symbol",
            "exchange_id",
            name="uq_market_instrument_symbol_exchange",
        ),
    )


# ============================================================
# CURRENT MARKET QUOTE
# ============================================================

class MarketQuote(Base):
    __tablename__ = "market_quotes"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
    )

    instrument_id = Column(
        BigInteger,
        ForeignKey(
            "market_instruments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    price = Column(
        Numeric(20, 8),
    )

    open = Column(
        Numeric(20, 8),
    )

    high = Column(
        Numeric(20, 8),
    )

    low = Column(
        Numeric(20, 8),
    )

    previous_close = Column(
        Numeric(20, 8),
    )

    change = Column(
        Numeric(20, 8),
    )

    change_percent = Column(
        Numeric(12, 6),
    )

    volume = Column(
        BigInteger,
    )

    market_cap = Column(
        Numeric(30, 2),
    )

    bid = Column(
        Numeric(20, 8),
    )

    ask = Column(
        Numeric(20, 8),
    )

    fifty_two_week_high = Column(
        Numeric(20, 8),
    )

    fifty_two_week_low = Column(
        Numeric(20, 8),
    )

    market_status = Column(
        String(30),
    )

    currency = Column(
        String(20),
    )

    data_source = Column(
        String(100),
    )

    quote_time = Column(
        DateTime(timezone=True),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    instrument = relationship(
        "MarketInstrument",
        back_populates="quote",
    )


# ============================================================
# HISTORICAL PRICE
# ============================================================

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
    )

    instrument_id = Column(
        BigInteger,
        ForeignKey(
            "market_instruments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    timeframe = Column(
        String(20),
        nullable=False,
        index=True,
    )

    candle_time = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    open = Column(
        Numeric(20, 8),
        nullable=False,
    )

    high = Column(
        Numeric(20, 8),
        nullable=False,
    )

    low = Column(
        Numeric(20, 8),
        nullable=False,
    )

    close = Column(
        Numeric(20, 8),
        nullable=False,
    )

    adjusted_close = Column(
        Numeric(20, 8),
    )

    volume = Column(
        BigInteger,
    )

    data_source = Column(
        String(100),
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    instrument = relationship(
        "MarketInstrument",
        back_populates="price_history",
    )

    __table_args__ = (
        UniqueConstraint(
            "instrument_id",
            "timeframe",
            "candle_time",
            name="uq_price_history_candle",
        ),

        Index(
            "idx_price_history_instrument_time",
            "instrument_id",
            "candle_time",
        ),
    )


# ============================================================
# FUNDAMENTALS
# ============================================================

class Fundamental(Base):
    __tablename__ = "fundamentals"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
    )

    instrument_id = Column(
        BigInteger,
        ForeignKey(
            "market_instruments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    market_cap = Column(
        Numeric(30, 2),
    )

    enterprise_value = Column(
        Numeric(30, 2),
    )

    revenue = Column(
        Numeric(30, 2),
    )

    net_income = Column(
        Numeric(30, 2),
    )

    gross_profit = Column(
        Numeric(30, 2),
    )

    operating_income = Column(
        Numeric(30, 2),
    )

    total_assets = Column(
        Numeric(30, 2),
    )

    total_liabilities = Column(
        Numeric(30, 2),
    )

    total_equity = Column(
        Numeric(30, 2),
    )

    cash = Column(
        Numeric(30, 2),
    )

    debt = Column(
        Numeric(30, 2),
    )

    eps = Column(
        Numeric(20, 8),
    )

    book_value_per_share = Column(
        Numeric(20, 8),
    )

    dividend_per_share = Column(
        Numeric(20, 8),
    )

    dividend_yield = Column(
        Numeric(12, 6),
    )

    pe_ratio = Column(
        Numeric(20, 8),
    )

    pb_ratio = Column(
        Numeric(20, 8),
    )

    ps_ratio = Column(
        Numeric(20, 8),
    )

    roe = Column(
        Numeric(12, 6),
    )

    roa = Column(
        Numeric(12, 6),
    )

    debt_to_equity = Column(
        Numeric(20, 8),
    )

    fiscal_year = Column(
        BigInteger,
    )

    fiscal_quarter = Column(
        BigInteger,
    )

    report_date = Column(
        Date,
    )

    data_source = Column(
        String(100),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    instrument = relationship(
        "MarketInstrument",
        back_populates="fundamentals",
    )

    __table_args__ = (
        UniqueConstraint(
            "instrument_id",
            "fiscal_year",
            "fiscal_quarter",
            name="uq_fundamentals_period",
        ),
    )


# ============================================================
# TECHNICAL INDICATORS
# ============================================================

class TechnicalIndicator(Base):
    __tablename__ = "technical_indicators"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
    )

    instrument_id = Column(
        BigInteger,
        ForeignKey(
            "market_instruments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    timeframe = Column(
        String(20),
        nullable=False,
    )

    calculation_time = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    sma_20 = Column(
        Numeric(20, 8),
    )

    sma_50 = Column(
        Numeric(20, 8),
    )

    sma_200 = Column(
        Numeric(20, 8),
    )

    ema_20 = Column(
        Numeric(20, 8),
    )

    ema_50 = Column(
        Numeric(20, 8),
    )

    ema_200 = Column(
        Numeric(20, 8),
    )

    rsi_14 = Column(
        Numeric(12, 6),
    )

    macd = Column(
        Numeric(20, 8),
    )

    macd_signal = Column(
        Numeric(20, 8),
    )

    macd_histogram = Column(
        Numeric(20, 8),
    )

    bollinger_upper = Column(
        Numeric(20, 8),
    )

    bollinger_middle = Column(
        Numeric(20, 8),
    )

    bollinger_lower = Column(
        Numeric(20, 8),
    )

    volatility = Column(
        Numeric(20, 8),
    )

    support = Column(
        Numeric(20, 8),
    )

    resistance = Column(
        Numeric(20, 8),
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    instrument = relationship(
        "MarketInstrument",
        back_populates="technical_indicators",
    )

    __table_args__ = (
        UniqueConstraint(
            "instrument_id",
            "timeframe",
            "calculation_time",
            name="uq_technical_indicator",
        ),
    )


# ============================================================
# MARKET NEWS
# ============================================================

class MarketNews(Base):
    __tablename__ = "market_news"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
    )

    instrument_id = Column(
        BigInteger,
        ForeignKey(
            "market_instruments.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    title = Column(
        String(500),
        nullable=False,
    )

    description = Column(
        Text,
    )

    url = Column(
        String(1000),
    )

    image_url = Column(
        String(1000),
    )

    source = Column(
        String(150),
    )

    sentiment = Column(
        String(30),
    )

    sentiment_score = Column(
        Numeric(12, 6),
    )

    published_at = Column(
        DateTime(timezone=True),
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    instrument = relationship(
        "MarketInstrument",
        back_populates="news",
    )


# ============================================================
# MARKET INDEX
# ============================================================

class MarketIndex(Base):
    __tablename__ = "market_indices"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
    )

    instrument_id = Column(
        BigInteger,
        ForeignKey(
            "market_instruments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    index_value = Column(
        Numeric(20, 8),
    )

    change = Column(
        Numeric(20, 8),
    )

    change_percent = Column(
        Numeric(12, 6),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    instrument = relationship(
        "MarketInstrument",
        back_populates="market_index",
    )