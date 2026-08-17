from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

# ---------------------------------
# Core
# ---------------------------------

from app.core.exceptions import (
    FinPilotException,
    finpilot_exception_handler,
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

# ---------------------------------
# Database
# ---------------------------------

from app.database.database import Base, engine

# ---------------------------------
# Middleware
# ---------------------------------

from app.middleware.logging_middleware import LoggingMiddleware

# ---------------------------------
# Existing Models
# ---------------------------------

from app.models.portfolio import Portfolio
from app.models.price_alert import PriceAlert
from app.models.stock import Stock
from app.models.user import User
from app.models.watchlist import Watchlist

# ---------------------------------
# Market Data Models
# ---------------------------------

from app.models.market_data import (
    Exchange,
    MarketInstrument,
    MarketQuote,
    PriceHistory,
    Fundamental,
    TechnicalIndicator,
    MarketNews,
    MarketIndex,
)

# ---------------------------------
# Routers
# ---------------------------------

from app.routers import (
    ai_router,
    dashboard_router,
    news_router,
    portfolio_router,
    price_alert_router,
    stock_router,
    user_router,
    watchlist_router,
)

from app.routers.market_data import (
    router as market_data_router,
)

from app.routers.market_ingestion import (
    router as market_ingestion_router,
)


# ============================================================
# DATABASE TABLE REGISTRATION
# ============================================================

Base.metadata.create_all(
    bind=engine
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="FinPilot API",
    description=(
        "AI-powered Stock Market Analysis Platform"
    ),
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "https://finpilot-frontend-dnba.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# LOGGING MIDDLEWARE
# ============================================================

app.add_middleware(
    LoggingMiddleware
)


# ============================================================
# EXCEPTION HANDLERS
# ============================================================

app.add_exception_handler(
    FinPilotException,
    finpilot_exception_handler,
)

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    general_exception_handler,
)


# ============================================================
# EXISTING FINPILOT ROUTERS
# ============================================================

app.include_router(
    user_router.router
)

app.include_router(
    stock_router.router
)

app.include_router(
    portfolio_router.router
)

app.include_router(
    watchlist_router.router
)

app.include_router(
    price_alert_router.router
)

app.include_router(
    news_router.router
)

app.include_router(
    dashboard_router.router
)

app.include_router(
    ai_router.router
)


# ============================================================
# MARKET DATA ROUTER
# ============================================================

app.include_router(
    market_data_router
)


# ============================================================
# MARKET DATA INGESTION ROUTER
# ============================================================

app.include_router(
    market_ingestion_router
)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "success": True,
        "message": "FinPilot Backend Running Successfully",
        "data": {
            "version": "1.0.0",
            "status": "running",
            "market_data": True,
            "market_ingestion": True,
        },
    }