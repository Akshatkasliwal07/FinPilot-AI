import yfinance as yf


def get_fundamental_data(symbol: str):

    try:

        stock = yf.Ticker(symbol)

        info = stock.info

        return {
            "company": info.get("longName"),
            "symbol": symbol,
            "current_price": info.get("currentPrice"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "eps": info.get("trailingEps"),
            "book_value": info.get("bookValue"),
            "price_to_book": info.get("priceToBook"),
            "return_on_equity": info.get("returnOnEquity"),
            "debt_to_equity": info.get("debtToEquity"),
            "profit_margin": info.get("profitMargins"),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "current_ratio": info.get("currentRatio"),
            "quick_ratio": info.get("quickRatio")
        }

    except Exception as e:

        return {
            "error": str(e)
        }