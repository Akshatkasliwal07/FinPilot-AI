from unittest.mock import patch


def test_create_stock(client):

    response = client.post(
        "/stocks",
        json={
            "symbol": "IBM",
            "company_name": "International Business Machines",
            "sector": "Technology",
            "exchange": "NYSE"
        }
    )

    assert response.status_code == 201, response.json()

    body = response.json()

    assert body["success"] is True
    assert body["data"]["symbol"] == "IBM"


def test_duplicate_stock(client):

    payload = {
        "symbol": "IBM",
        "company_name": "International Business Machines",
        "sector": "Technology",
        "exchange": "NYSE"
    }

    first_response = client.post(
        "/stocks",
        json=payload
    )

    print(
        "FIRST STOCK RESPONSE:",
        first_response.status_code,
        first_response.json()
    )

    assert first_response.status_code == 201, (
        first_response.json()
    )

    second_response = client.post(
        "/stocks",
        json=payload
    )

    print(
        "DUPLICATE STOCK RESPONSE:",
        second_response.status_code,
        second_response.json()
    )

    assert second_response.status_code == 400

    second_body = second_response.json()

    assert second_body["success"] is False
    assert second_body["error"] == "Stock already exists."


def test_get_stocks_with_pagination(client):

    create_response = client.post(
        "/stocks",
        json={
            "symbol": "IBM",
            "company_name": "International Business Machines",
            "sector": "Technology",
            "exchange": "NYSE"
        }
    )

    print(
        "PAGINATION CREATE RESPONSE:",
        create_response.status_code,
        create_response.json()
    )

    assert create_response.status_code == 201, (
        create_response.json()
    )

    response = client.get(
        "/stocks?page=1&limit=10"
    )

    print(
        "PAGINATION RESPONSE:",
        response.status_code,
        response.json()
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"]["total"] == 1
    assert body["data"]["page"] == 1
    assert body["data"]["limit"] == 10
    assert body["data"]["total_pages"] == 1
    assert len(body["data"]["items"]) == 1
    assert body["data"]["items"][0]["symbol"] == "IBM"


def test_filter_stocks_by_symbol(client):

    ibm_response = client.post(
        "/stocks",
        json={
            "symbol": "IBM",
            "company_name": "International Business Machines",
            "sector": "Technology",
            "exchange": "NYSE"
        }
    )

    assert ibm_response.status_code == 201, (
        ibm_response.json()
    )

    apple_response = client.post(
        "/stocks",
        json={
            "symbol": "AAPL",
            "company_name": "Apple Inc.",
            "sector": "Technology",
            "exchange": "NASDAQ"
        }
    )

    assert apple_response.status_code == 201, (
        apple_response.json()
    )

    response = client.get(
        "/stocks?page=1&limit=10&symbol=IBM"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["data"]["total"] == 1
    assert len(body["data"]["items"]) == 1
    assert body["data"]["items"][0]["symbol"] == "IBM"


def test_filter_stocks_by_sector(client):

    ibm_response = client.post(
        "/stocks",
        json={
            "symbol": "IBM",
            "company_name": "International Business Machines",
            "sector": "Technology",
            "exchange": "NYSE"
        }
    )

    assert ibm_response.status_code == 201, (
        ibm_response.json()
    )

    bank_response = client.post(
        "/stocks",
        json={
            "symbol": "JPM",
            "company_name": "JPMorgan Chase",
            "sector": "Financial Services",
            "exchange": "NYSE"
        }
    )

    assert bank_response.status_code == 201, (
        bank_response.json()
    )

    response = client.get(
        "/stocks?page=1&limit=10&sector=Technology"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["data"]["total"] == 1
    assert len(body["data"]["items"]) == 1
    assert body["data"]["items"][0]["symbol"] == "IBM"
    assert body["data"]["items"][0]["sector"] == "Technology"


@patch(
    "app.services.stock_service."
    "AlphaVantageAPI.get_stock_quote"
)
def test_get_live_stock(
    mock_get_quote,
    client
):

    mock_get_quote.return_value = {
        "01. symbol": "IBM",
        "05. price": "214.1900"
    }

    response = client.get(
        "/stocks/live/IBM"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"]["01. symbol"] == "IBM"
    assert body["data"]["05. price"] == "214.1900"

    mock_get_quote.assert_called_once_with(
        "IBM"
    )