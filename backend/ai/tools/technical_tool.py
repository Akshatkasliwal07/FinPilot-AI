import yfinance as yf
import pandas as pd

from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
from ta.volatility import BollingerBands


def get_technical_data(symbol: str):
    """
    Fetch historical stock data and calculate
    technical indicators.
    """

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="6mo")

        if df.empty:
            return {
                "error": f"No historical data found for {symbol}"
            }

        # ------------------------
        # Moving Averages
        # ------------------------
        df["SMA20"] = SMAIndicator(
            close=df["Close"],
            window=20
        ).sma_indicator()

        df["SMA50"] = SMAIndicator(
            close=df["Close"],
            window=50
        ).sma_indicator()

        # ------------------------
        # RSI
        # ------------------------
        df["RSI"] = RSIIndicator(
            close=df["Close"],
            window=14
        ).rsi()

        # ------------------------
        # MACD
        # ------------------------
        macd = MACD(close=df["Close"])

        df["MACD"] = macd.macd()
        df["MACD_SIGNAL"] = macd.macd_signal()

        # ------------------------
        # Bollinger Bands
        # ------------------------
        bb = BollingerBands(close=df["Close"])

        df["BB_UPPER"] = bb.bollinger_hband()
        df["BB_LOWER"] = bb.bollinger_lband()

        latest = df.iloc[-1]

        return {

            "company": ticker.info.get("longName"),

            "symbol": symbol,

            "current_price": round(float(latest["Close"]), 2),

            "sma20": round(float(latest["SMA20"]), 2),

            "sma50": round(float(latest["SMA50"]), 2),

            "rsi": round(float(latest["RSI"]), 2),

            "macd": round(float(latest["MACD"]), 2),

            "macd_signal": round(float(latest["MACD_SIGNAL"]), 2),

            "bollinger_upper": round(float(latest["BB_UPPER"]), 2),

            "bollinger_lower": round(float(latest["BB_LOWER"]), 2),

            "volume": int(latest["Volume"])

        }

    except Exception as e:
        return {
            "error": str(e)
        }