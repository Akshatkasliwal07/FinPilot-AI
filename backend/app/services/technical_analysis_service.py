from __future__ import annotations

import pandas as pd


class TechnicalAnalysisService:

    @staticmethod
    def calculate_indicators(history: list[dict]) -> dict:
        """
        Calculate technical indicators from historical OHLCV data.

        Expected input:
        [
            {
                "date": "...",
                "open": 0,
                "high": 0,
                "low": 0,
                "close": 0,
                "volume": 0
            }
        ]
        """

        # -------------------------------------------------
        # Validate input
        # -------------------------------------------------

        if not history:
            return {
                "success": False,
                "message": "Historical data is required.",
                "data": {},
            }

        # -------------------------------------------------
        # Create DataFrame
        # -------------------------------------------------

        df = pd.DataFrame(history)

        required_columns = [
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]

        missing = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing:
            return {
                "success": False,
                "message": (
                    f"Missing columns: {', '.join(missing)}"
                ),
                "data": {},
            }

        # -------------------------------------------------
        # Convert values to numeric
        # -------------------------------------------------

        for column in required_columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

        df = df.dropna(
            subset=required_columns
        ).reset_index(drop=True)

        if df.empty:
            return {
                "success": False,
                "message": "No valid historical data available.",
                "data": {},
            }

        # -------------------------------------------------
        # Sort by date if date exists
        # -------------------------------------------------

        if "date" in df.columns:
            df["date"] = pd.to_datetime(
                df["date"],
                errors="coerce",
            )

            df = (
                df.sort_values("date")
                .reset_index(drop=True)
            )

        close = df["close"]

        # =================================================
        # SMA 20
        # =================================================

        sma_20 = close.rolling(
            window=20
        ).mean()

        # =================================================
        # SMA 50
        # =================================================

        sma_50 = close.rolling(
            window=50
        ).mean()

        # =================================================
        # EMA 12
        # =================================================

        ema_12 = close.ewm(
            span=12,
            adjust=False,
        ).mean()

        # =================================================
        # EMA 26
        # =================================================

        ema_26 = close.ewm(
            span=26,
            adjust=False,
        ).mean()

        # =================================================
        # MACD
        # =================================================

        macd = ema_12 - ema_26

        # MACD signal line
        macd_signal_line = macd.ewm(
            span=9,
            adjust=False,
        ).mean()

        # MACD histogram
        macd_histogram = (
            macd - macd_signal_line
        )

        # =================================================
        # RSI 14
        # =================================================

        delta = close.diff()

        gains = delta.clip(
            lower=0
        )

        losses = -delta.clip(
            upper=0
        )

        average_gain = gains.rolling(
            window=14
        ).mean()

        average_loss = losses.rolling(
            window=14
        ).mean()

        rs = average_gain / average_loss.replace(
            0,
            float("nan"),
        )

        rsi = 100 - (
            100 / (1 + rs)
        )

        # =================================================
        # Daily Returns
        # =================================================

        daily_returns = close.pct_change()

        # =================================================
        # 20-Day Volatility
        # =================================================

        volatility = (
            daily_returns
            .rolling(window=20)
            .std()
            * 100
        )

        # =================================================
        # Volume SMA 20
        # =================================================

        volume_sma_20 = (
            df["volume"]
            .rolling(window=20)
            .mean()
        )

        # =================================================
        # Latest Values
        # =================================================

        latest_close = float(
            close.iloc[-1]
        )

        latest_sma_20 = (
            TechnicalAnalysisService._safe_float(
                sma_20.iloc[-1]
            )
        )

        latest_sma_50 = (
            TechnicalAnalysisService._safe_float(
                sma_50.iloc[-1]
            )
        )

        latest_rsi = (
            TechnicalAnalysisService._safe_float(
                rsi.iloc[-1]
            )
        )

        latest_macd = (
            TechnicalAnalysisService._safe_float(
                macd.iloc[-1]
            )
        )

        latest_macd_signal = (
            TechnicalAnalysisService._safe_float(
                macd_signal_line.iloc[-1]
            )
        )

        latest_macd_histogram = (
            TechnicalAnalysisService._safe_float(
                macd_histogram.iloc[-1]
            )
        )

        latest_volatility = (
            TechnicalAnalysisService._safe_float(
                volatility.iloc[-1]
            )
        )

        latest_volume_average = (
            TechnicalAnalysisService._safe_float(
                volume_sma_20.iloc[-1]
            )
        )

        latest_volume = float(
            df["volume"].iloc[-1]
        )

        # =================================================
        # Trend
        # =================================================

        trend = "NEUTRAL"

        if (
            latest_sma_20 is not None
            and latest_sma_50 is not None
        ):
            if (
                latest_close > latest_sma_20
                and latest_sma_20 > latest_sma_50
            ):
                trend = "BULLISH"

            elif (
                latest_close < latest_sma_20
                and latest_sma_20 < latest_sma_50
            ):
                trend = "BEARISH"

        elif latest_sma_20 is not None:

            if latest_close > latest_sma_20:
                trend = "BULLISH"

            elif latest_close < latest_sma_20:
                trend = "BEARISH"

        # =================================================
        # RSI Signal
        # =================================================

        rsi_signal = "NEUTRAL"

        if latest_rsi is not None:

            if latest_rsi >= 70:
                rsi_signal = "OVERBOUGHT"

            elif latest_rsi <= 30:
                rsi_signal = "OVERSOLD"

            elif latest_rsi > 50:
                rsi_signal = "BULLISH"

            else:
                rsi_signal = "BEARISH"

        # =================================================
        # MACD Direction
        # =================================================

        macd_direction = "NEUTRAL"

        if (
            latest_macd is not None
            and latest_macd_signal is not None
        ):

            if latest_macd > latest_macd_signal:
                macd_direction = "BULLISH"

            elif latest_macd < latest_macd_signal:
                macd_direction = "BEARISH"

        # =================================================
        # Volume Signal
        # =================================================

        volume_signal = "NORMAL"

        volume_ratio = None

        if (
            latest_volume_average is not None
            and latest_volume_average > 0
        ):

            volume_ratio = (
                latest_volume
                / latest_volume_average
            )

            if volume_ratio >= 1.5:
                volume_signal = "HIGH"

            elif volume_ratio <= 0.7:
                volume_signal = "LOW"

        # =================================================
        # Support / Resistance
        # =================================================

        recent_data = df.tail(20)

        support = float(
            recent_data["low"].min()
        )

        resistance = float(
            recent_data["high"].max()
        )

        # =================================================
        # Price Position
        # =================================================

        price_vs_sma20 = None

        if latest_sma_20 is not None:
            price_vs_sma20 = round(
                (
                    (
                        latest_close
                        - latest_sma_20
                    )
                    / latest_sma_20
                )
                * 100,
                4,
            )

        price_vs_sma50 = None

        if latest_sma_50 is not None:
            price_vs_sma50 = round(
                (
                    (
                        latest_close
                        - latest_sma_50
                    )
                    / latest_sma_50
                )
                * 100,
                4,
            )

        # =================================================
        # MACD Histogram Direction
        # =================================================

        macd_histogram_direction = "NEUTRAL"

        if latest_macd_histogram is not None:

            if latest_macd_histogram > 0:
                macd_histogram_direction = "POSITIVE"

            elif latest_macd_histogram < 0:
                macd_histogram_direction = "NEGATIVE"

        # =================================================
        # Return Result
        # =================================================

        return {
            "success": True,
            "message": (
                "Technical indicators calculated successfully."
            ),
            "data": {

                # Price
                "latest_close": latest_close,

                # Moving averages
                "sma_20": latest_sma_20,
                "sma_50": latest_sma_50,

                # RSI
                "rsi_14": latest_rsi,
                "rsi_signal": rsi_signal,

                # MACD
                "macd": latest_macd,
                "macd_signal": latest_macd_signal,
                "macd_histogram": latest_macd_histogram,
                "macd_direction": macd_direction,
                "macd_histogram_direction": (
                    macd_histogram_direction
                ),

                # Volatility
                "volatility_20d": latest_volatility,

                # Volume
                "latest_volume": latest_volume,
                "volume_average_20d": (
                    latest_volume_average
                ),
                "volume_ratio": (
                    round(volume_ratio, 4)
                    if volume_ratio is not None
                    else None
                ),
                "volume_signal": volume_signal,

                # Trend
                "trend": trend,

                # Support / Resistance
                "support": support,
                "resistance": resistance,

                # Price position
                "price_vs_sma20_percent": (
                    price_vs_sma20
                ),
                "price_vs_sma50_percent": (
                    price_vs_sma50
                ),
            },
        }

    # =====================================================
    # Safe Float Helper
    # =====================================================

    @staticmethod
    def _safe_float(value):
        """
        Convert pandas/numpy values safely to Python float.

        Returns None when the value cannot be calculated.
        """

        if pd.isna(value):
            return None

        return round(
            float(value),
            4,
        )