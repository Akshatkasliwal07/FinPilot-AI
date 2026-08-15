import requests

from app.core.config import ALPHA_VANTAGE_API_KEY

BASE_URL = "https://www.alphavantage.co/query"


class AlphaVantageAPI:

    @staticmethod
    def get_stock_quote(symbol: str):

        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY,
        }

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        # Alpha Vantage API limit / information response
        if "Information" in data:
            print("Alpha Vantage:", data["Information"])
            return None

        # API error response
        if "Error Message" in data:
            print("Alpha Vantage Error:", data["Error Message"])
            return None

        return data.get("Global Quote", {})

    @staticmethod
    def get_daily_history(symbol: str):

        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "compact",
            "apikey": ALPHA_VANTAGE_API_KEY,
        }

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        if "Information" in data:
            print("Alpha Vantage:", data["Information"])
            return None

        if "Error Message" in data:
            print("Alpha Vantage Error:", data["Error Message"])
            return None

        return data.get("Time Series (Daily)", {})