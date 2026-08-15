import pandas as pd

from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.volatility import BollingerBands


class TechnicalAnalysis:

    @staticmethod
    def calculate(history: dict):

        rows = []

        for date, values in history.items():
            rows.append({
                "date": date,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": float(values["5. volume"])
            })

        df = pd.DataFrame(rows)

        # Oldest → Newest
        df = df.sort_values("date")

        # RSI
        df["rsi"] = RSIIndicator(
            close=df["close"],
            window=14
        ).rsi()

        # SMA
        df["sma20"] = SMAIndicator(
            close=df["close"],
            window=20
        ).sma_indicator()

        df["sma50"] = SMAIndicator(
            close=df["close"],
            window=50
        ).sma_indicator()

        # EMA
        df["ema20"] = EMAIndicator(
            close=df["close"],
            window=20
        ).ema_indicator()

        # MACD
        macd = MACD(df["close"])

        df["macd"] = macd.macd()

        # Bollinger Bands
        bb = BollingerBands(df["close"])

        df["bb_upper"] = bb.bollinger_hband()
        df["bb_lower"] = bb.bollinger_lband()

        latest = df.iloc[-1]

        return {
    "rsi": float(round(latest["rsi"], 2)),
    "sma20": float(round(latest["sma20"], 2)),
    "sma50": float(round(latest["sma50"], 2)),
    "ema20": float(round(latest["ema20"], 2)),
    "macd": float(round(latest["macd"], 2)),
    "bollinger_upper": float(round(latest["bb_upper"], 2)),
    "bollinger_lower": float(round(latest["bb_lower"], 2))
}