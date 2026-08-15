from app.api.news_api import NewsAPI
from app.ai.sentiment_analyzer import SentimentAnalyzer
from app.core.exceptions import FinPilotException

class NewsService:

    # -----------------------------------------
    # Get Stock News
    # -----------------------------------------

    @staticmethod
    def get_stock_news(
        symbol: str,
        limit: int = 10
    ):

        stock_symbol = symbol.strip().upper()

        if not stock_symbol:
            raise FinPilotException(
                "Stock symbol is required.",
                400
            )

        if limit <= 0:
            raise FinPilotException(
                "Limit must be greater than zero.",
                400
            )

        if limit > 50:
            raise FinPilotException(
                "Limit cannot be greater than 50.",
                400
            )

        articles = NewsAPI.get_stock_news(
            stock_symbol,
            limit
        )

        sentiment_result = (
            SentimentAnalyzer.analyze_articles(
                articles
            )
        )

        return {
            "symbol": stock_symbol,
            "overall_sentiment": sentiment_result[
                "overall_sentiment"
            ],
            "confidence": sentiment_result[
                "confidence"
            ],
            "articles": sentiment_result[
                "articles"
            ]
        }

    # -----------------------------------------
    # Get General Market News
    # -----------------------------------------

    @staticmethod
    def get_market_news(
        limit: int = 10
    ):

        if limit <= 0:
            raise FinPilotException(
                "Limit must be greater than zero.",
                400
            )

        if limit > 50:
            raise FinPilotException(
                "Limit cannot be greater than 50.",
                400
            )

        articles = NewsAPI.get_market_news(
            limit
        )

        sentiment_result = (
            SentimentAnalyzer.analyze_articles(
                articles
            )
        )

        return {
            "symbol": "MARKET",
            "overall_sentiment": sentiment_result[
                "overall_sentiment"
            ],
            "confidence": sentiment_result[
                "confidence"
            ],
            "articles": sentiment_result[
                "articles"
            ]
        }