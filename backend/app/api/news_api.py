import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from app.core.exceptions import FinPilotException


class NewsAPI:
    """
    Marketaux financial news provider.

    Supports:
    - Indian NSE/BSE stocks
    - Dynamic Marketaux entity lookup
    - Alternate NSE symbols such as TCS-BL.NS
    - Stock-specific news only
    - Recent-news filtering
    - Safe handling when no recent news exists
    - General Indian market news
    - Free-plan article limit
    """

    NEWS_URL = "https://api.marketaux.com/v1/news/all"

    ENTITY_SEARCH_URL = (
        "https://api.marketaux.com/v1/entity/search"
    )

    # Refresh news cache every 5 minutes.
    CACHE_TTL = 5 * 60

    # Your current Marketaux plan allows 3 articles.
    MAX_ARTICLES = 3

    _cache: dict[
        str,
        tuple[float, list[dict[str, Any]]]
    ] = {}

    # =========================================================
    # API TOKEN
    # =========================================================

    @staticmethod
    def _get_token() -> str:
        token = os.getenv(
            "MARKETAUX_API_TOKEN",
            ""
        ).strip()

        if not token:
            raise FinPilotException(
                "Market news service is not configured.",
                503
            )

        return token

    # =========================================================
    # CACHE
    # =========================================================

    @classmethod
    def _get_cached(
        cls,
        key: str
    ):
        cached = cls._cache.get(key)

        if cached is None:
            return None

        created_at, data = cached

        if (
            time.time() - created_at
            < cls.CACHE_TTL
        ):
            return data

        cls._cache.pop(
            key,
            None
        )

        return None

    @classmethod
    def _set_cached(
        cls,
        key: str,
        data: list[dict[str, Any]]
    ):
        cls._cache[key] = (
            time.time(),
            data
        )

    # =========================================================
    # NORMALIZE ARTICLE
    # =========================================================

    @staticmethod
    def _normalize_article(
        article: dict[str, Any]
    ) -> dict[str, Any]:

        source = (
            article.get("source")
            or article.get("source_name")
            or article.get("domain")
            or "Unknown"
        )

        if isinstance(source, dict):
            source = (
                source.get("name")
                or source.get("domain")
                or "Unknown"
            )

        return {
            "title": str(
                article.get("title")
                or ""
            ).strip(),

            "summary": str(
                article.get("description")
                or article.get("snippet")
                or ""
            ).strip(),

            "source": str(source),

            "time_published": str(
                article.get("published_at")
                or ""
            ),

            "url": str(
                article.get("url")
                or ""
            ),
        }

    # =========================================================
    # ENTITY SEARCH
    # =========================================================

    @classmethod
    def _search_entities(
        cls,
        symbol: str
    ) -> list[dict[str, Any]]:

        token = cls._get_token()

        try:
            response = requests.get(
                cls.ENTITY_SEARCH_URL,
                params={
                    "api_token": token,
                    "search": symbol,
                    "page": 1,
                },
                timeout=15,
            )

        except requests.RequestException as exc:
            print(
                "Marketaux entity search error:",
                exc
            )
            return []

        if response.status_code != 200:
            print(
                "Marketaux entity search HTTP error:",
                response.status_code
            )
            print(
                response.text[:500]
            )
            return []

        try:
            payload = response.json()
        except ValueError:
            return []

        entities = payload.get(
            "data",
            []
        )

        if not isinstance(
            entities,
            list
        ):
            return []

        return [
            entity
            for entity in entities
            if isinstance(
                entity,
                dict
            )
        ]

    # =========================================================
    # FIND VERIFIED INDIAN EQUITY
    # =========================================================

    @classmethod
    def _find_indian_entity(
        cls,
        symbol: str
    ):

        symbol_upper = (
            symbol
            .strip()
            .upper()
        )

        entities = cls._search_entities(
            symbol_upper
        )

        if not entities:
            print(
                f"No Marketaux entities found "
                f"for {symbol_upper}"
            )
            return None

        candidates = []

        for entity in entities:

            entity_symbol = str(
                entity.get(
                    "symbol",
                    ""
                )
            ).upper().strip()

            entity_country = str(
                entity.get(
                    "country",
                    ""
                )
            ).lower().strip()

            entity_type = str(
                entity.get(
                    "type",
                    ""
                )
            ).lower().strip()

            # Only Indian equities.
            if entity_country != "in":
                continue

            if entity_type != "equity":
                continue

            # -------------------------------------------------
            # Priority 1:
            # Exact NSE symbol
            #
            # Example:
            # TCS -> TCS.NS
            # -------------------------------------------------

            if entity_symbol == (
                f"{symbol_upper}.NS"
            ):
                candidates.append(
                    (
                        1,
                        entity
                    )
                )
                continue

            # -------------------------------------------------
            # Priority 2:
            # Alternate NSE symbols
            #
            # Example:
            # TCS-BL.NS
            # TCS-BE.NS
            # -------------------------------------------------

            if (
                entity_symbol.startswith(
                    f"{symbol_upper}-"
                )
                and entity_symbol.endswith(
                    ".NS"
                )
            ):
                candidates.append(
                    (
                        2,
                        entity
                    )
                )
                continue

            # -------------------------------------------------
            # Priority 3:
            # Exact BSE symbol
            # -------------------------------------------------

            if entity_symbol == (
                f"{symbol_upper}.BO"
            ):
                candidates.append(
                    (
                        3,
                        entity
                    )
                )
                continue

            # -------------------------------------------------
            # Priority 4:
            # Alternate BSE symbols
            # -------------------------------------------------

            if (
                entity_symbol.startswith(
                    f"{symbol_upper}-"
                )
                and entity_symbol.endswith(
                    ".BO"
                )
            ):
                candidates.append(
                    (
                        4,
                        entity
                    )
                )

        if not candidates:
            print(
                f"No verified Indian equity "
                f"entity found for {symbol_upper}"
            )
            return None

        candidates.sort(
            key=lambda item: item[0]
        )

        selected = candidates[0][1]

        print(
            "Verified Marketaux entity:",
            selected.get("symbol"),
            "-",
            selected.get("name"),
            "-",
            selected.get("country")
        )

        return selected

    # =========================================================
    # RECENT DATE
    # =========================================================

    @staticmethod
    def _recent_date(
        days: int = 30
    ) -> str:

        date_value = (
            datetime.now(
                timezone.utc
            )
            - timedelta(days=days)
        )

        return date_value.strftime(
            "%Y-%m-%dT%H:%M"
        )

    # =========================================================
    # REQUEST STOCK NEWS
    # =========================================================

    @classmethod
    def _request_symbol_news(
        cls,
        marketaux_symbol: str,
        limit: int
    ) -> list[dict[str, Any]]:

        token = cls._get_token()

        # Never exceed the current plan limit.
        safe_limit = min(
            max(
                1,
                int(limit)
            ),
            cls.MAX_ARTICLES
        )

        params = {
            "api_token": token,

            # Exact verified Marketaux entity.
            "symbols": marketaux_symbol,

            # Indian news.
            "countries": "in",

            # Only articles actually linked to entities.
            "filter_entities": "true",

            "must_have_entities": "true",

            "group_similar": "true",

            "language": "en",

            # Only recent stock news.
            "published_after": cls._recent_date(
                days=30
            ),

            "limit": safe_limit,

            "page": 1,
        }

        try:
            response = requests.get(
                cls.NEWS_URL,
                params=params,
                timeout=15,
            )

        except requests.RequestException as exc:
            print(
                "Marketaux news connection error:",
                exc
            )
            return []

        if response.status_code != 200:
            print(
                "Marketaux news HTTP error:",
                response.status_code
            )
            print(
                response.text[:1000]
            )
            return []

        try:
            payload = response.json()
        except ValueError:
            return []

        if payload.get("error"):
            print(
                "Marketaux API error:",
                payload.get("error")
            )
            return []

        raw_articles = payload.get(
            "data",
            []
        )

        if not isinstance(
            raw_articles,
            list
        ):
            return []

        articles = []

        for article in raw_articles:

            if not isinstance(
                article,
                dict
            ):
                continue

            # =================================================
            # SAFETY CHECK
            #
            # Marketaux must explicitly identify the requested
            # entity in the article.
            # =================================================

            entities = article.get(
                "entities",
                []
            )

            if isinstance(
                entities,
                list
            ) and entities:

                matched = False

                for entity in entities:

                    if not isinstance(
                        entity,
                        dict
                    ):
                        continue

                    article_symbol = str(
                        entity.get(
                            "symbol",
                            ""
                        )
                    ).upper().strip()

                    if article_symbol == (
                        marketaux_symbol.upper()
                    ):
                        matched = True
                        break

                if not matched:
                    continue

            normalized = (
                cls._normalize_article(
                    article
                )
            )

            if not normalized["title"]:
                continue

            articles.append(
                normalized
            )

        return articles[:safe_limit]

    # =========================================================
    # STOCK NEWS
    # =========================================================

    @classmethod
    def get_stock_news(
        cls,
        symbol: str,
        limit: int = 10
    ):

        stock_symbol = (
            symbol
            .strip()
            .upper()
        )

        if not stock_symbol:
            raise FinPilotException(
                "Stock symbol is required.",
                400
            )

        # Respect Marketaux plan.
        safe_limit = min(
            max(
                1,
                int(limit)
            ),
            cls.MAX_ARTICLES
        )

        cache_key = (
            f"stock:{stock_symbol}:{safe_limit}"
        )

        cached = cls._get_cached(
            cache_key
        )

        if cached is not None:
            return cached

        # -----------------------------------------------------
        # Find verified Indian entity.
        # -----------------------------------------------------

        entity = cls._find_indian_entity(
            stock_symbol
        )

        if not entity:

            print(
                f"No verified Indian Marketaux "
                f"entity for {stock_symbol}"
            )

            # IMPORTANT:
            # Do NOT use generic search.
            #
            # Generic search can return another company
            # with the same abbreviation.
            #

            cls._set_cached(
                cache_key,
                []
            )

            return []

        marketaux_symbol = str(
            entity.get(
                "symbol",
                ""
            )
        ).upper().strip()

        if not marketaux_symbol:

            cls._set_cached(
                cache_key,
                []
            )

            return []

        # -----------------------------------------------------
        # Fetch exact entity news.
        # -----------------------------------------------------

        articles = cls._request_symbol_news(
            marketaux_symbol,
            safe_limit
        )

        cls._set_cached(
            cache_key,
            articles
        )

        print(
            f"Fetched {len(articles)} recent articles "
            f"for {stock_symbol} "
            f"using {marketaux_symbol}"
        )

        return articles

    # =========================================================
    # GENERAL INDIAN MARKET NEWS
    # =========================================================

    @classmethod
    def get_market_news(
        cls,
        limit: int = 10
    ):

        safe_limit = min(
            max(
                1,
                int(limit)
            ),
            cls.MAX_ARTICLES
        )

        cache_key = (
            f"market:india:{safe_limit}"
        )

        cached = cls._get_cached(
            cache_key
        )

        if cached is not None:
            return cached

        token = cls._get_token()

        params = {
            "api_token": token,

            "countries": "in",

            "filter_entities": "true",

            "must_have_entities": "true",

            "group_similar": "true",

            "language": "en",

            # General market news can be more recent.
            "published_after": cls._recent_date(
                days=7
            ),

            "limit": safe_limit,

            "page": 1,
        }

        try:
            response = requests.get(
                cls.NEWS_URL,
                params=params,
                timeout=15,
            )

        except requests.RequestException as exc:

            print(
                "Marketaux market-news error:",
                exc
            )

            cls._set_cached(
                cache_key,
                []
            )

            return []

        if response.status_code != 200:

            print(
                "Marketaux market-news HTTP error:",
                response.status_code
            )

            print(
                response.text[:500]
            )

            cls._set_cached(
                cache_key,
                []
            )

            return []

        try:
            payload = response.json()
        except ValueError:

            cls._set_cached(
                cache_key,
                []
            )

            return []

        if payload.get("error"):

            print(
                "Marketaux market-news API error:",
                payload.get("error")
            )

            cls._set_cached(
                cache_key,
                []
            )

            return []

        raw_articles = payload.get(
            "data",
            []
        )

        if not isinstance(
            raw_articles,
            list
        ):

            cls._set_cached(
                cache_key,
                []
            )

            return []

        articles = []

        for article in raw_articles:

            if not isinstance(
                article,
                dict
            ):
                continue

            normalized = (
                cls._normalize_article(
                    article
                )
            )

            if not normalized["title"]:
                continue

            articles.append(
                normalized
            )

        articles = articles[
            :safe_limit
        ]

        cls._set_cached(
            cache_key,
            articles
        )

        return articles