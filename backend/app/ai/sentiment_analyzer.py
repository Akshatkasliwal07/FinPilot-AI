class SentimentAnalyzer:

    POSITIVE_WORDS = {
        "growth",
        "profit",
        "profits",
        "record",
        "strong",
        "surge",
        "surges",
        "gain",
        "gains",
        "bullish",
        "upgrade",
        "upgraded",
        "outperform",
        "expansion",
        "partnership",
        "innovation",
        "beat",
        "beats",
        "success",
        "successful"
    }

    NEGATIVE_WORDS = {
        "loss",
        "losses",
        "decline",
        "declines",
        "drop",
        "drops",
        "fall",
        "falls",
        "bearish",
        "downgrade",
        "downgraded",
        "underperform",
        "lawsuit",
        "risk",
        "weak",
        "miss",
        "misses",
        "cut",
        "cuts",
        "layoff",
        "layoffs"
    }

    @staticmethod
    def analyze_text(text: str):

        normalized_text = text.lower()

        positive_score = sum(
            1
            for word in SentimentAnalyzer.POSITIVE_WORDS
            if word in normalized_text
        )

        negative_score = sum(
            1
            for word in SentimentAnalyzer.NEGATIVE_WORDS
            if word in normalized_text
        )

        score = positive_score - negative_score

        if score > 0:
            sentiment = "Bullish"

        elif score < 0:
            sentiment = "Bearish"

        else:
            sentiment = "Neutral"

        return {
            "sentiment": sentiment,
            "score": score
        }

    @staticmethod
    def analyze_articles(articles: list):

        analyzed_articles = []
        total_score = 0

        for article in articles:

            title = article.get("title", "")
            summary = article.get("summary", "")

            combined_text = f"{title} {summary}"

            result = SentimentAnalyzer.analyze_text(
                combined_text
            )

            total_score += result["score"]

            analyzed_articles.append({
                "title": title,
                "source": article.get("source", "Unknown"),
                "published_at": article.get(
                    "time_published",
                    ""
                ),
                "url": article.get("url", ""),
                "sentiment": result["sentiment"]
            })

        article_count = len(analyzed_articles)

        if total_score > 0:
            overall_sentiment = "Bullish"

        elif total_score < 0:
            overall_sentiment = "Bearish"

        else:
            overall_sentiment = "Neutral"

        confidence = min(
            95,
            60 + abs(total_score) * 5
        )

        if article_count == 0:
            confidence = 0

        return {
            "overall_sentiment": overall_sentiment,
            "confidence": confidence,
            "articles": analyzed_articles
        }