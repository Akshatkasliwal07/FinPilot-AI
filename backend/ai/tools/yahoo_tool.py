import yfinance as yf


def get_stock_data(symbol: str):

    symbol = symbol.strip().upper()

    ticker = yf.Ticker(symbol)

    history = ticker.history(
        period="5d",
        auto_adjust=False
    )

    if history.empty:
        raise Exception(f"No data found for {symbol}")

    fast = ticker.fast_info

    return {
        "company": symbol,
        "symbol": symbol,
        "current_price": float(history["Close"].iloc[-1]),
        "open": float(history["Open"].iloc[-1]),
        "high": float(history["High"].iloc[-1]),
        "low": float(history["Low"].iloc[-1]),
        "close": float(history["Close"].iloc[-1]),
        "volume": int(history["Volume"].iloc[-1]),

        "market_cap": fast.get("market_cap"),
        "currency": fast.get("currency"),
        "exchange": fast.get("exchange"),
        "year_high": fast.get("year_high"),
        "year_low": fast.get("year_low")
    }