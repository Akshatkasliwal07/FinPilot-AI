import yfinance as yf


def get_company_profile(symbol: str):

    try:

        stock = yf.Ticker(symbol)

        info = stock.info

        return {
            "company_name": info.get("longName"),
            "symbol": symbol,
            "business_summary": info.get("longBusinessSummary"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "country": info.get("country"),
            "city": info.get("city"),
            "website": info.get("website"),
            "employees": info.get("fullTimeEmployees"),
            "market_cap": info.get("marketCap"),
            "exchange": info.get("exchange"),
            "currency": info.get("currency"),
        }

    except Exception as e:

        return {
            "error": str(e)
        }