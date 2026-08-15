from unittest.mock import patch


def create_authenticated_user(client):

    signup_response = client.post(
        "/users/signup",
        json={
            "name": "Dashboard Test User",
            "email": "dashboard@example.com",
            "password": "Test@12345"
        }
    )

    assert signup_response.status_code == 201

    login_response = client.post(
        "/users/login",
        data={
            "username": "dashboard@example.com",
            "password": "Test@12345"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


@patch(
    "app.services.portfolio_service."
    "AlphaVantageAPI.get_stock_quote"
)
def test_dashboard_with_user_data(
    mock_get_stock_quote,
    client
):

    mock_get_stock_quote.return_value = {
        "05. price": "214.19"
    }

    headers = create_authenticated_user(client)

    portfolio_response = client.post(
        "/portfolio/",
        headers=headers,
        json={
            "stock_symbol": "IBM",
            "quantity": 5,
            "purchase_price": 200
        }
    )

    assert portfolio_response.status_code == 201

    watchlist_response = client.post(
        "/watchlist/",
        headers=headers,
        json={
            "stock_symbol": "IBM"
        }
    )

    assert watchlist_response.status_code == 201

    alert_response = client.post(
        "/price-alerts/",
        headers=headers,
        json={
            "stock_symbol": "IBM",
            "target_price": 220,
            "condition": "above"
        }
    )

    assert alert_response.status_code == 201

    response = client.get(
        "/dashboard",
        headers=headers
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == (
        "Dashboard fetched successfully."
    )

    data = body["data"]

    assert data["user"]["name"] == (
        "Dashboard Test User"
    )
    assert data["user"]["email"] == (
        "dashboard@example.com"
    )

    assert data["portfolio"]["total_invested"] == 1000
    assert data["portfolio"]["current_value"] == 1070.95
    assert data["portfolio"]["profit_loss"] == 70.95
    assert data["portfolio"]["return_percentage"] == 7.1
    assert data["portfolio"]["holdings"] == 1

    assert data["watchlist_count"] == 1
    assert len(data["watchlist"]) == 1
    assert data["watchlist"][0]["stock_symbol"] == "IBM"

    assert data["alerts_count"] == 1
    assert len(data["price_alerts"]) == 1
    assert data["price_alerts"][0]["stock_symbol"] == "IBM"


def test_dashboard_requires_authentication(client):

    response = client.get(
        "/dashboard"
    )

    assert response.status_code == 401