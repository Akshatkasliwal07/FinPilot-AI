import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base, get_db

# Import all models so every table is registered.
from app.models.user import User
from app.models.stock import Stock
from app.models.portfolio import Portfolio
from app.models.watchlist import Watchlist
from app.models.price_alert import PriceAlert

from app.main import app

# Import the exact get_db objects used inside routers.
from app.routers.user_router import get_db as user_get_db
from app.routers.stock_router import get_db as stock_get_db
from app.routers.portfolio_router import get_db as portfolio_get_db
from app.routers.watchlist_router import get_db as watchlist_get_db
from app.routers.price_alert_router import get_db as price_alert_get_db
from app.routers.dashboard_router import get_db as dashboard_get_db


TEST_DATABASE_FILE = "./test_finpilot.db"
TEST_DATABASE_URL = (
    f"sqlite:///{TEST_DATABASE_FILE}"
)


test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=test_engine
)


def override_get_db():

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.rollback()
        db.close()


def apply_database_overrides():

    dependencies = [
        get_db,
        user_get_db,
        stock_get_db,
        portfolio_get_db,
        watchlist_get_db,
        price_alert_get_db,
        dashboard_get_db
    ]

    for dependency in dependencies:
        app.dependency_overrides[
            dependency
        ] = override_get_db


apply_database_overrides()


@pytest.fixture(autouse=True)
def reset_test_database():

    Base.metadata.drop_all(
        bind=test_engine
    )

    Base.metadata.create_all(
        bind=test_engine
    )

    yield

    Base.metadata.drop_all(
        bind=test_engine
    )


@pytest.fixture
def client():

    apply_database_overrides()

    with TestClient(app) as test_client:
        yield test_client


def pytest_sessionfinish(
    session,
    exitstatus
):

    test_engine.dispose()

    if os.path.exists(TEST_DATABASE_FILE):
        os.remove(TEST_DATABASE_FILE)