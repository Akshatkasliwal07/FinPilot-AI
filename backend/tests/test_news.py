from unittest.mock import patch


@patch(
    "app.services.news_service."
    "NewsService.get_stock_news"
)
def test_get_stock_news_success(
    mock_get_stock_news,
    client
):

    mock_get_stock_news.return_value = {
        "symbol": "IBM",
        "overall_sentiment": "Bullish",
        "confidence": 95,
        "articles": [
            {
                "title": "IBM test article",
                "source": "Test Source",
                "published_at": "20260727T120000",
                "url": "https://example.com/ibm",
                "sentiment": "Bullish"
            }
        ]
    }

    response = client.get(
        "/news/IBM?limit=10"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == (
        "News for IBM fetched successfully."
    )

    assert body["data"]["symbol"] == "IBM"
    assert body["data"]["overall_sentiment"] == "Bullish"
    assert body["data"]["confidence"] == 95
    assert len(body["data"]["articles"]) == 1
    assert body["data"]["articles"][0]["title"] == (
        "IBM test article"
    )

    mock_get_stock_news.assert_called_once_with(
        symbol="IBM",
        limit=10
    )


@patch(
    "app.services.news_service."
    "NewsService.get_stock_news"
)
def test_news_limit_validation(
    mock_get_stock_news,
    client
):

    response = client.get(
        "/news/IBM?limit=0"
    )

    assert response.status_code == 422

    mock_get_stock_news.assert_not_called()