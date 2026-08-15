import traceback

from fastapi import APIRouter, Depends, HTTPException

from app.ai.ai_schema import (
    AIAnalysisRequest,
    AIAnalysisResponse,
)

from app.ai.ai_service import analyze_stock

from app.ai.recommendation_engine import (
    RecommendationEngine,
)

from app.models.user import User

from app.schemas.common_schema import (
    APIResponse,
)

from app.services.stock_service import (
    StockService,
)

from app.services.technical_analysis_service import (
    TechnicalAnalysisService,
)

from app.services.news_service import (
    NewsService,
)

from app.utils.auth import (
    get_current_user,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


# =========================================================
# EXISTING AI ANALYSIS
# =========================================================

@router.post(
    "/analyze",
    response_model=APIResponse[AIAnalysisResponse],
    summary="Analyze Stock with FinPilot AI",
)
def analyze_ai_stock(
    request: AIAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    try:

        analysis = analyze_stock(request)

        return {
            "success": True,
            "message": (
                "AI analysis completed successfully."
            ),
            "data": analysis,
        }

    except Exception as exc:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                f"{type(exc).__name__}: "
                f"{str(exc)}"
            ),
        )


# =========================================================
# AUTOMATIC STOCK DECISION
# =========================================================
#
# Example:
#
# GET /ai/decision/IRCTC
#
# User does NOT need to provide:
# - current price
# - historical data
# - RSI
# - MACD
# - SMA
# - news
#
# FinPilot collects everything automatically.
#
# =========================================================

@router.get(
    "/decision/{symbol}",
    summary="Get Automatic Buy/Sell/Hold Decision",
)
def automatic_stock_decision(
    symbol: str,
    current_user: User = Depends(get_current_user),
):

    try:

        # =================================================
        # 1. CLEAN SYMBOL
        # =================================================

        stock_symbol = (
            symbol
            .strip()
            .upper()
        )

        if not stock_symbol:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Stock symbol is required."
                ),
            )


        # =================================================
        # 2. GET LIVE STOCK DATA
        # =================================================

        live_data = (
            StockService.get_live_stock(
                stock_symbol
            )
        )

        if not live_data:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Unable to find live "
                    f"data for {stock_symbol}."
                ),
            )


        # =================================================
        # 3. GET CURRENT PRICE
        # =================================================

        try:

            current_price = float(
                live_data[
                    "05. price"
                ]
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ):

            raise HTTPException(
                status_code=500,
                detail=(
                    "Unable to read the "
                    "current stock price."
                ),
            )


        # =================================================
        # 4. GET HISTORICAL DATA
        # =================================================

        history_data = (
            StockService.get_stock_history(
                symbol=stock_symbol,
                period="1y",
            )
        )

        history = (
            history_data.get(
                "items",
                []
            )
        )

        if not history:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Historical data "
                    f"not available for "
                    f"{stock_symbol}."
                ),
            )


        # =================================================
        # 5. TECHNICAL ANALYSIS
        # =================================================

        technical_result = (
            TechnicalAnalysisService
            .calculate_indicators(
                history
            )
        )

        if not technical_result.get(
            "success",
            False
        ):

            raise HTTPException(
                status_code=500,
                detail=(
                    technical_result.get(
                        "message",
                        "Technical analysis failed.",
                    )
                ),
            )

        indicators = (
            technical_result.get(
                "data",
                {}
            )
        )


        # =================================================
        # 6. GET STOCK-SPECIFIC NEWS
        # =================================================

        stock_news = []

        stock_news_sentiment = (
            "Neutral"
        )

        try:

            stock_news_result = (
                NewsService.get_stock_news(
                    symbol=stock_symbol,
                    limit=10,
                )
            )

            stock_news = (
                stock_news_result.get(
                    "articles",
                    []
                )
            )

            stock_news_sentiment = (
                stock_news_result.get(
                    "overall_sentiment",
                    "Neutral",
                )
            )

        except Exception as news_error:

            print(
                f"Stock news error "
                f"for {stock_symbol}:",
                news_error,
            )

            # News failure should NOT
            # stop stock analysis.

            stock_news = []

            stock_news_sentiment = (
                "Neutral"
            )


        # =================================================
        # 7. GET GENERAL MARKET NEWS
        # =================================================

        market_news_sentiment = (
            "Neutral"
        )

        try:

            market_news_result = (
                NewsService.get_market_news(
                    limit=10
                )
            )

            market_news_sentiment = (
                market_news_result.get(
                    "overall_sentiment",
                    "Neutral",
                )
            )

        except Exception as market_error:

            print(
                "Market news error:",
                market_error,
            )

            market_news_sentiment = (
                "Neutral"
            )


        # =================================================
        # 8. COMBINE NEWS SENTIMENT
        # =================================================

        if (
            stock_news_sentiment
            == "Bullish"
            and
            market_news_sentiment
            == "Bullish"
        ):

            final_news_sentiment = (
                "Bullish"
            )

        elif (
            stock_news_sentiment
            == "Bearish"
            and
            market_news_sentiment
            == "Bearish"
        ):

            final_news_sentiment = (
                "Bearish"
            )

        elif (
            stock_news_sentiment
            == "Bullish"
            and
            market_news_sentiment
            != "Bearish"
        ):

            final_news_sentiment = (
                "Bullish"
            )

        elif (
            stock_news_sentiment
            == "Bearish"
            and
            market_news_sentiment
            != "Bullish"
        ):

            final_news_sentiment = (
                "Bearish"
            )

        else:

            final_news_sentiment = (
                "Neutral"
            )


        # =================================================
        # 9. ADD NEWS INFORMATION TO INDICATORS
        # =================================================

        indicators = {
            **indicators,

            "stock_news_sentiment":
                stock_news_sentiment,

            "market_news_sentiment":
                market_news_sentiment,

            "news_sentiment":
                final_news_sentiment,
        }


        # =================================================
        # 10. RUN RECOMMENDATION ENGINE
        # =================================================

        try:

            decision = (
                RecommendationEngine.analyze(
                    price=current_price,
                    indicators=indicators,
                )
            )

        except TypeError:

            # If the existing engine only accepts
            # price + indicators, this keeps it
            # compatible with your current code.

            decision = (
                RecommendationEngine.analyze(
                    current_price,
                    indicators,
                )
            )


        # =================================================
        # 11. NORMALIZE RESULT
        # =================================================

        recommendation = (
            decision.get(
                "recommendation",
                "HOLD",
            )
        )

        confidence = int(
            decision.get(
                "confidence",
                0,
            )
        )

        reason = (
            decision.get(
                "reason",
                "Insufficient information "
                "for a strong recommendation.",
            )
        )

        score = decision.get(
            "score",
            0,
        )

        risk_level = decision.get(
            "risk_level",
            "MODERATE",
        )


        # =================================================
        # 12. DIRECT ONE-LINE ACTION
        # =================================================

        recommendation_upper = (
            str(
                recommendation
            )
            .strip()
            .upper()
        )

        if recommendation_upper == "BUY":

            action = (
                f"BUY {stock_symbol} now, "
                f"but monitor it closely."
            )

        elif recommendation_upper == "SELL":

            action = (
                f"SELL {stock_symbol}; "
                f"downside risk is currently elevated."
            )

        elif recommendation_upper == "HOLD":

            action = (
                f"HOLD {stock_symbol} "
                f"and wait for a stronger signal."
            )

        else:

            action = (
                f"WAIT on {stock_symbol}; "
                f"there is no strong buy signal yet."
            )


        # =================================================
        # 13. RETURN COMPLETE FINPILOT DECISION
        # =================================================

        return {

            "success": True,

            "message": (
                f"Automatic FinPilot decision "
                f"completed for {stock_symbol}."
            ),

            "data": {

                # -----------------------------------------
                # BASIC
                # -----------------------------------------

                "symbol":
                    stock_symbol,

                "current_price":
                    current_price,

                # -----------------------------------------
                # DIRECT ANSWER
                # -----------------------------------------

                "action":
                    action,

                "recommendation":
                    recommendation_upper,

                "confidence":
                    confidence,

                # -----------------------------------------
                # EXPLANATION
                # -----------------------------------------

                "reason":
                    reason,

                "risk_level":
                    risk_level,

                "technical_score":
                    score,

                # -----------------------------------------
                # SIGNAL INFORMATION
                # -----------------------------------------

                "trend":
                    indicators.get(
                        "trend"
                    ),

                "rsi":
                    indicators.get(
                        "rsi"
                    ),

                "sma20":
                    indicators.get(
                        "sma20"
                    ),

                "sma50":
                    indicators.get(
                        "sma50"
                    ),

                "macd":
                    indicators.get(
                        "macd"
                    ),

                # -----------------------------------------
                # NEWS
                # -----------------------------------------

                "stock_news_sentiment":
                    stock_news_sentiment,

                "market_news_sentiment":
                    market_news_sentiment,

                "news_sentiment":
                    final_news_sentiment,

                "news_count":
                    len(stock_news),

                # -----------------------------------------
                # DATA SOURCE
                # -----------------------------------------

                "data_source":
                    live_data.get(
                        "data_source",
                        "Yahoo Finance",
                    ),
            },
        }


    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except HTTPException:

        raise

    except Exception as exc:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                f"{type(exc).__name__}: "
                f"{str(exc)}"
            ),
        )