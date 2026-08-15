import os
import requests

from dotenv import load_dotenv


load_dotenv()


class EODHDProvider:

    BASE_URL = os.getenv(
        "EODHD_BASE_URL",
        "https://eodhd.com/api",
    )

    API_KEY = os.getenv(
        "EODHD_API_KEY"
    )

    # ========================================================
    # INDIAN EXCHANGE MAPPING
    # ========================================================

    INDIAN_EXCHANGES = {
        "NSE": "XNSE",
        "BSE": "XBOM",
    }

    ALLOWED_PROVIDER_EXCHANGES = {
        "XNSE",
        "XBOM",
    }

    # ========================================================
    # COMMON REQUEST
    # ========================================================

    @classmethod
    def _request(
        cls,
        endpoint: str,
        params: dict | None = None,
    ):

        if not cls.API_KEY:
            raise RuntimeError(
                "EODHD_API_KEY is not configured."
            )

        request_params = {
            "api_token": cls.API_KEY,
            "fmt": "json",
        }

        if params:
            request_params.update(params)

        url = (
            f"{cls.BASE_URL.rstrip('/')}/"
            f"{endpoint.lstrip('/')}"
        )

        response = requests.get(
            url,
            params=request_params,
            timeout=30,
        )

        # Give a useful error instead of a generic
        # requests exception.
        if not response.ok:

            try:
                error_data = response.json()
            except ValueError:
                error_data = response.text

            raise RuntimeError(
                f"EODHD request failed "
                f"(HTTP {response.status_code}): "
                f"{error_data}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "EODHD returned an invalid JSON response."
            ) from exc

        if isinstance(data, dict):

            if data.get("error"):
                raise RuntimeError(
                    str(data["error"])
                )

        return data

    # ========================================================
    # NORMALIZE INDIAN TICKER
    # ========================================================

    @classmethod
    def _normalize_ticker(
        cls,
        ticker: str,
        default_exchange: str = "NSE",
    ):

        if not ticker:
            raise ValueError(
                "Ticker is required."
            )

        ticker = ticker.strip().upper()

        # ----------------------------------------------------
        # Bare symbol
        #
        # RELIANCE -> RELIANCE.XNSE
        # ----------------------------------------------------

        if "." not in ticker:

            provider_exchange = (
                cls.INDIAN_EXCHANGES.get(
                    default_exchange.upper()
                )
            )

            if not provider_exchange:
                raise ValueError(
                    "Only NSE and BSE are supported."
                )

            return (
                f"{ticker}.{provider_exchange}"
            )

        # ----------------------------------------------------
        # Symbol already contains exchange
        # ----------------------------------------------------

        symbol, exchange = ticker.rsplit(
            ".",
            1,
        )

        exchange = exchange.upper()

        # User-friendly exchange names
        if exchange == "NSE":
            exchange = "XNSE"

        elif exchange == "BSE":
            exchange = "XBOM"

        # ----------------------------------------------------
        # Only Indian exchanges
        # ----------------------------------------------------

        if exchange not in (
            "XNSE",
            "XBOM",
        ):
            raise ValueError(
                "FinPilot supports only "
                "Indian NSE and BSE stocks."
            )

        if not symbol:
            raise ValueError(
                "Stock symbol is required."
            )

        return (
            f"{symbol}.{exchange}"
        )

    # ========================================================
    # REAL-TIME / LATEST QUOTE
    # ========================================================

    @classmethod
    def get_quote(
        cls,
        ticker: str,
    ):

        normalized_ticker = (
            cls._normalize_ticker(
                ticker
            )
        )

        return cls._request(
            f"real-time/{normalized_ticker}"
        )

    # ========================================================
    # END OF DAY HISTORY
    # ========================================================

    @classmethod
    def get_history(
        cls,
        ticker: str,
        from_date: str | None = None,
        to_date: str | None = None,
        period: str = "d",
    ):

        normalized_ticker = (
            cls._normalize_ticker(
                ticker
            )
        )

        params = {
            "period": period,
            "order": "a",
        }

        if from_date:
            params["from"] = from_date

        if to_date:
            params["to"] = to_date

        return cls._request(
            f"eod/{normalized_ticker}",
            params,
        )

    # ========================================================
    # FUNDAMENTALS
    # ========================================================

    @classmethod
    def get_fundamentals(
        cls,
        ticker: str,
    ):

        normalized_ticker = (
            cls._normalize_ticker(
                ticker
            )
        )

        return cls._request(
            f"fundamentals/{normalized_ticker}"
        )

    # ========================================================
    # NEWS
    # ========================================================

    @classmethod
    def get_news(
        cls,
        ticker: str | None = None,
        limit: int = 20,
    ):

        params = {
            "limit": limit,
        }

        if ticker:

            normalized_ticker = (
                cls._normalize_ticker(
                    ticker
                )
            )

            params["s"] = normalized_ticker

        return cls._request(
            "news",
            params,
        )

    # ========================================================
    # TECHNICAL INDICATOR
    # ========================================================

    @classmethod
    def get_technical(
        cls,
        ticker: str,
        function: str,
        period: int = 14,
    ):

        normalized_ticker = (
            cls._normalize_ticker(
                ticker
            )
        )

        return cls._request(
            f"technical/{normalized_ticker}",
            {
                "function": function,
                "period": period,
            },
        )

    # ========================================================
    # EXCHANGE SYMBOL LIST
    # ========================================================
    #
    # NOTE:
    # We are keeping this method for compatibility with
    # existing code.
    #
    # Your current stock-import process does NOT depend
    # on this endpoint because EODHD was returning 404
    # for the exchange-symbol-list request.
    #
    # ========================================================

    @classmethod
    def get_exchange_symbols(
        cls,
        exchange_code: str,
    ):

        exchange_code = (
            exchange_code.strip().upper()
        )

        provider_exchange = (
            cls.INDIAN_EXCHANGES.get(
                exchange_code
            )
        )

        if not provider_exchange:
            raise ValueError(
                "Only NSE and BSE are supported."
            )

        return cls._request(
            f"exchange-symbol-list/"
            f"{provider_exchange}"
        )

    # ========================================================
    # SEARCH
    # ========================================================

    @classmethod
    def search(
        cls,
        query: str,
    ):

        if not query:
            return []

        result = cls._request(
            "search",
            {
                "q": query.strip(),
            },
        )

        # ----------------------------------------------------
        # Filter search results to India only
        # ----------------------------------------------------

        if not isinstance(
            result,
            list,
        ):
            return result

        indian_results = []

        for item in result:

            if not isinstance(
                item,
                dict,
            ):
                continue

            exchange = str(
                item.get("Exchange")
                or item.get("exchange")
                or item.get("ExchangeCode")
                or ""
            ).upper()

            country = str(
                item.get("Country")
                or item.get("country")
                or ""
            ).upper()

            currency = str(
                item.get("Currency")
                or item.get("currency")
                or ""
            ).upper()

            if (
                exchange in (
                    "XNSE",
                    "XBOM",
                    "NSE",
                    "BSE",
                )
                or country == "INDIA"
                or currency == "INR"
            ):
                indian_results.append(
                    item
                )

        return indian_results

    # ========================================================
    # EXCHANGES LIST
    # ========================================================

    @classmethod
    def get_exchanges(cls):

        exchanges = cls._request(
            "exchanges-list"
        )

        if not isinstance(
            exchanges,
            list,
        ):
            return []

        indian_exchanges = []

        for exchange in exchanges:

            if not isinstance(
                exchange,
                dict,
            ):
                continue

            code = str(
                exchange.get("Code")
                or exchange.get("code")
                or ""
            ).upper()

            country = str(
                exchange.get("Country")
                or exchange.get("country")
                or ""
            ).upper()

            name = str(
                exchange.get("Name")
                or exchange.get("name")
                or ""
            ).upper()

            # ------------------------------------------------
            # Only India
            # ------------------------------------------------

            if (
                code in (
                    "NSE",
                    "BSE",
                    "XNSE",
                    "XBOM",
                    "IN.NSE",
                    "IN.BSE",
                )
                or country == "INDIA"
                or "NATIONAL STOCK EXCHANGE" in name
                or "BOMBAY STOCK EXCHANGE" in name
            ):
                indian_exchanges.append(
                    exchange
                )

        return indian_exchanges