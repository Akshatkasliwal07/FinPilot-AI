import math

import yfinance as yf
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.stock import Stock
from app.models.watchlist import Watchlist

from app.repositories.stock_repository import StockRepository
from app.repositories.watchlist_repository import (
    WatchlistRepository,
)

from app.schemas.watchlist_schema import WatchlistCreate
from app.core.exceptions import FinPilotException


class WatchlistService:

    # ============================================================
    # RESOLVE STOCK FROM LOCAL DATABASE OR LIVE MARKET DATA
    # ============================================================

    @staticmethod
    def _resolve_stock(
        db: Session,
        stock_symbol: str,
    ):
        """
        Resolve an Indian NSE/BSE stock.

        1. Check the existing local stocks table.
        2. If not found, dynamically verify the symbol using
           Yahoo Finance.
        3. Create a local Stock record automatically.
        4. Return the Stock object.

        This allows any valid NSE/BSE stock to be added to
        the watchlist without manually inserting every stock
        into the database.
        """

        symbol = (
            stock_symbol
            .strip()
            .upper()
        )

        # --------------------------------------------------------
        # 1. CHECK EXISTING LOCAL STOCK
        # --------------------------------------------------------

        stock = (
            WatchlistRepository.get_stock_by_symbol(
                db,
                symbol,
            )
        )

        if stock:
            return stock

        # --------------------------------------------------------
        # 2. DYNAMIC YAHOO FINANCE RESOLUTION
        # --------------------------------------------------------

        yahoo_symbol = None
        exchange = None
        company_name = symbol

        # Try NSE first.
        candidates = [
            (f"{symbol}.NS", "NSE"),
            (f"{symbol}.BO", "BSE"),
        ]

        for candidate, candidate_exchange in candidates:

            try:
                ticker = yf.Ticker(
                    candidate
                )

                history = ticker.history(
                    period="5d",
                    interval="1d",
                    auto_adjust=False,
                )

                if (
                    history is not None
                    and not history.empty
                ):
                    yahoo_symbol = candidate
                    exchange = candidate_exchange
                    break

            except Exception:
                continue

        # --------------------------------------------------------
        # 3. FALLBACK TO YAHOO SEARCH
        # --------------------------------------------------------

        if not yahoo_symbol:

            try:
                search = yf.Search(
                    symbol,
                    max_results=10,
                    news_count=0,
                    lists_count=0,
                    include_cb=False,
                    include_nav_links=False,
                    include_research=False,
                    include_cultural_assets=False,
                    enable_fuzzy_query=True,
                    recommended=0,
                    timeout=15,
                    raise_errors=False,
                )

                quotes = (
                    getattr(
                        search,
                        "quotes",
                        None,
                    )
                    or []
                )

                for item in quotes:

                    if not isinstance(
                        item,
                        dict,
                    ):
                        continue

                    candidate = str(
                        item.get("symbol")
                        or ""
                    ).strip().upper()

                    if candidate.endswith(
                        ".NS"
                    ):
                        yahoo_symbol = candidate
                        exchange = "NSE"

                    elif candidate.endswith(
                        ".BO"
                    ):
                        yahoo_symbol = candidate
                        exchange = "BSE"

                    else:
                        continue

                    base_symbol = (
                        candidate.rsplit(
                            ".",
                            1,
                        )[0]
                    )

                    if (
                        base_symbol == symbol
                        or candidate.startswith(
                            symbol + "."
                        )
                    ):
                        company_name = (
                            item.get(
                                "longname"
                            )
                            or item.get(
                                "longName"
                            )
                            or item.get(
                                "shortname"
                            )
                            or item.get(
                                "shortName"
                            )
                            or symbol
                        )

                        break

            except Exception:
                pass

        # --------------------------------------------------------
        # 4. STOCK NOT FOUND
        # --------------------------------------------------------

        if not yahoo_symbol:

            raise FinPilotException(
                (
                    f"Stock {symbol} could not be "
                    "found on NSE or BSE."
                ),
                404,
            )

        # --------------------------------------------------------
        # 5. GET COMPANY NAME IF POSSIBLE
        # --------------------------------------------------------

        if company_name == symbol:

            try:
                ticker = yf.Ticker(
                    yahoo_symbol
                )

                info = ticker.info or {}

                company_name = (
                    info.get("longName")
                    or info.get("shortName")
                    or symbol
                )

            except Exception:
                company_name = symbol

        # --------------------------------------------------------
        # 6. CREATE LOCAL STOCK RECORD
        # --------------------------------------------------------

        new_stock = Stock(
            symbol=symbol,
            company_name=str(
                company_name
            ),
            sector=None,
            exchange=exchange,
        )

        try:

            stock = (
                StockRepository.create_stock(
                    db,
                    new_stock,
                )
            )

            return stock

        except IntegrityError:

            # Another request may have created
            # the same stock at the same time.

            db.rollback()

            stock = (
                WatchlistRepository
                .get_stock_by_symbol(
                    db,
                    symbol,
                )
            )

            if stock:
                return stock

            raise FinPilotException(
                (
                    f"Unable to create stock "
                    f"{symbol} in the database."
                ),
                500,
            )

    # ============================================================
    # ADD STOCK TO WATCHLIST
    # ============================================================

    @staticmethod
    def add_stock(
        db: Session,
        user_id: int,
        watchlist: WatchlistCreate,
    ):

        stock_symbol = (
            watchlist.stock_symbol
            .strip()
            .upper()
        )

        if not stock_symbol:

            raise FinPilotException(
                "Stock symbol is required.",
                400,
            )

        # --------------------------------------------------------
        # RESOLVE ANY VALID NSE/BSE STOCK
        # --------------------------------------------------------

        stock = (
            WatchlistService._resolve_stock(
                db,
                stock_symbol,
            )
        )

        # --------------------------------------------------------
        # CHECK DUPLICATE
        # --------------------------------------------------------

        existing = (
            WatchlistRepository
            .get_by_user_and_stock(
                db,
                user_id,
                stock.id,
            )
        )

        if existing:

            raise FinPilotException(
                (
                    f"{stock_symbol} is already "
                    "in your watchlist."
                ),
                400,
            )

        # --------------------------------------------------------
        # CREATE WATCHLIST ENTRY
        # --------------------------------------------------------

        new_watchlist = Watchlist(
            user_id=user_id,
            stock_id=stock.id,
        )

        try:

            created_item = (
                WatchlistRepository
                .create_watchlist(
                    db,
                    new_watchlist,
                )
            )

        except IntegrityError:

            db.rollback()

            existing = (
                WatchlistRepository
                .get_by_user_and_stock(
                    db,
                    user_id,
                    stock.id,
                )
            )

            if existing:

                raise FinPilotException(
                    (
                        f"{stock_symbol} is already "
                        "in your watchlist."
                    ),
                    400,
                )

            raise FinPilotException(
                (
                    "Unable to add stock to "
                    "your watchlist."
                ),
                500,
            )

        return {
            "id": created_item.id,
            "stock_symbol": stock.symbol,
            "created_at": created_item.created_at,
        }

    # ============================================================
    # GET USER WATCHLIST
    # ============================================================

    @staticmethod
    def get_watchlist(
        db: Session,
        user_id: int,
        page: int = 1,
        limit: int = 10,
        symbol: str | None = None,
    ):

        result = (
            WatchlistRepository
            .get_user_watchlist(
                db=db,
                user_id=user_id,
                page=page,
                limit=limit,
                symbol=symbol,
            )
        )

        total = result["total"]

        total_pages = (
            math.ceil(
                total / limit
            )
            if total > 0
            else 0
        )

        items = []

        for item in result["items"]:

            items.append(
                {
                    "id": item.id,
                    "stock_symbol": (
                        item.stock.symbol
                    ),
                    "created_at": (
                        item.created_at
                    ),
                }
            )

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
        }

    # ============================================================
    # DELETE WATCHLIST ITEM
    # ============================================================

    @staticmethod
    def delete_stock(
        db: Session,
        user_id: int,
        watchlist_id: int,
    ):

        watchlist = (
            WatchlistRepository
            .get_watchlist_by_id(
                db,
                watchlist_id,
            )
        )

        if not watchlist:

            raise FinPilotException(
                "Watchlist item not found.",
                404,
            )

        # --------------------------------------------------------
        # SECURITY CHECK
        # --------------------------------------------------------

        if watchlist.user_id != user_id:

            raise FinPilotException(
                (
                    "You cannot delete another "
                    "user's watchlist item."
                ),
                403,
            )

        return (
            WatchlistRepository
            .delete_watchlist(
                db,
                watchlist,
            )
        )