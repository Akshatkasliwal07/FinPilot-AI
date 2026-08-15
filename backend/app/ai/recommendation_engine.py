from __future__ import annotations

from typing import Any


class RecommendationEngine:

    """
    FinPilot deterministic decision engine.

    This engine evaluates:
    - RSI
    - MACD
    - SMA20
    - SMA50
    - EMA20
    - price trend
    - volatility
    - news sentiment

    It deliberately avoids making a decision when
    the supplied market data is insufficient.
    """

    @staticmethod
    def _number(
        value: Any,
        default: float | None = None
    ) -> float | None:

        try:
            if value is None:
                return default

            number = float(value)

            if number != number:
                return default

            return number

        except (
            TypeError,
            ValueError
        ):
            return default

    @classmethod
    def analyze(
        cls,
        price: float,
        indicators: dict | None = None,
        news_sentiment: str = "Neutral",
        market_sentiment: str = "Neutral",
    ) -> dict:

        indicators = indicators or {}

        current_price = cls._number(
            price
        )

        if current_price is None or current_price <= 0:

            return {
                "recommendation": "WAIT",
                "confidence": 0,
                "score": 0,
                "reason": (
                    "WAIT — live price data is "
                    "currently unavailable."
                ),
                "risk_level": "High",
            }

        score = 0
        reasons = []

        data_points = 0

        # =====================================================
        # RSI
        # =====================================================

        rsi = cls._number(
            indicators.get("rsi_14")
            if "rsi_14" in indicators
            else indicators.get("rsi")
        )

        if rsi is not None:

            data_points += 1

            if rsi < 30:

                score += 12

                reasons.append(
                    "RSI is oversold"
                )

            elif rsi < 45:

                score += 5

                reasons.append(
                    "RSI is recovering"
                )

            elif rsi <= 60:

                score += 8

                reasons.append(
                    "RSI supports positive momentum"
                )

            elif rsi <= 70:

                score += 2

                reasons.append(
                    "RSI remains positive"
                )

            else:

                score -= 12

                reasons.append(
                    "RSI indicates overbought conditions"
                )

        # =====================================================
        # MACD
        # =====================================================

        macd = cls._number(
            indicators.get("macd")
        )

        macd_direction = str(
            indicators.get(
                "macd_direction",
                ""
            )
        ).lower()

        if macd is not None:

            data_points += 1

            if (
                macd > 0
                or "bullish" in macd_direction
                or "positive" in macd_direction
            ):

                score += 15

                reasons.append(
                    "MACD supports bullish momentum"
                )

            else:

                score -= 15

                reasons.append(
                    "MACD shows bearish momentum"
                )

        # =====================================================
        # PRICE VS SMA20
        # =====================================================

        sma20 = cls._number(
            indicators.get("sma20")
            if "sma20" in indicators
            else indicators.get("sma_20")
        )

        if sma20 is not None:

            data_points += 1

            if current_price > sma20:

                score += 12

                reasons.append(
                    "price is above SMA20"
                )

            else:

                score -= 12

                reasons.append(
                    "price is below SMA20"
                )

        # =====================================================
        # PRICE VS SMA50
        # =====================================================

        sma50 = cls._number(
            indicators.get("sma50")
            if "sma50" in indicators
            else indicators.get("sma_50")
        )

        if sma50 is not None:

            data_points += 1

            if current_price > sma50:

                score += 10

                reasons.append(
                    "price is above SMA50"
                )

            else:

                score -= 10

                reasons.append(
                    "price is below SMA50"
                )

        # =====================================================
        # EMA20
        # =====================================================

        ema20 = cls._number(
            indicators.get("ema20")
            if "ema20" in indicators
            else indicators.get("ema_20")
        )

        if ema20 is not None:

            data_points += 1

            if current_price > ema20:

                score += 8

            else:

                score -= 8

        # =====================================================
        # MACD HISTOGRAM
        # =====================================================

        histogram = cls._number(
            indicators.get(
                "macd_histogram"
            )
        )

        if histogram is not None:

            data_points += 1

            if histogram > 0:

                score += 8

            elif histogram < 0:

                score -= 8

        # =====================================================
        # VOLATILITY
        # =====================================================

        volatility = cls._number(
            indicators.get(
                "volatility_20d"
            )
        )

        if volatility is not None:

            if volatility > 8:

                reasons.append(
                    "volatility is elevated"
                )

            elif volatility < 3:

                reasons.append(
                    "volatility is relatively low"
                )

        # =====================================================
        # NEWS SENTIMENT
        # =====================================================

        news = str(
            news_sentiment or "Neutral"
        ).lower()

        if news == "bullish":

            score += 10
            reasons.append(
                "recent news sentiment is bullish"
            )

        elif news == "bearish":

            score -= 10
            reasons.append(
                "recent news sentiment is bearish"
            )

        # =====================================================
        # MARKET SENTIMENT
        # =====================================================

        market = str(
            market_sentiment or "Neutral"
        ).lower()

        if market == "bullish":

            score += 5

        elif market == "bearish":

            score -= 5

        # =====================================================
        # NOT ENOUGH DATA
        # =====================================================

        if data_points < 2:

            return {
                "recommendation": "WAIT",
                "confidence": 25,
                "score": score,
                "reason": (
                    "WAIT — there is not enough reliable "
                    "technical data to make a strong "
                    "decision right now."
                ),
                "risk_level": "High",
            }

        # =====================================================
        # DECISION
        # =====================================================

        if score >= 35:

            recommendation = "BUY"

        elif score <= -30:

            recommendation = "SELL"

        elif score >= 10:

            recommendation = "HOLD"

        elif score <= -10:

            recommendation = "WAIT"

        else:

            recommendation = "WAIT"

        # =====================================================
        # CONFIDENCE
        # =====================================================

        confidence = min(
            95,
            max(
                30,
                50 + abs(score)
            )
        )

        # Reduce confidence if news is missing.
        if not news_sentiment:

            confidence -= 5

        confidence = max(
            20,
            min(
                95,
                confidence
            )
        )

        # =====================================================
        # RISK
        # =====================================================

        if volatility is not None and volatility > 8:

            risk_level = "High"

        elif volatility is not None and volatility > 5:

            risk_level = "Moderate"

        else:

            risk_level = "Low"

        # =====================================================
        # DIRECT ONE-SENTENCE MESSAGE
        # =====================================================

        evidence = ", ".join(
            reasons[:3]
        )

        if recommendation == "BUY":

            reason = (
                f"BUY — {evidence}; "
                f"the overall setup is bullish, "
                f"but risk remains."
            )

        elif recommendation == "SELL":

            reason = (
                f"SELL — {evidence}; "
                f"the overall setup is bearish."
            )

        elif recommendation == "HOLD":

            reason = (
                f"HOLD — {evidence}; "
                f"the current trend is mixed but "
                f"does not show a strong exit signal."
            )

        else:

            reason = (
                f"WAIT — {evidence}; "
                f"there is not enough confirmation "
                f"for a fresh entry right now."
            )

        return {
            "recommendation": recommendation,
            "confidence": int(confidence),
            "score": int(score),
            "reason": reason,
            "risk_level": risk_level,
        }