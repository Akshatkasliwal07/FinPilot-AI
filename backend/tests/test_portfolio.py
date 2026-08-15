def create_authenticated_user(client):

    client.post(
        "/users/signup",
        json={
            "name": "Portfolio Test User",
            "email": "portfolio@example.com",
            "password": "Test@12345"
        }
    )

    login_response = client.post(
        "/users/login",
        data={
            "username": "portfolio@example.com",
            "password": "Test@12345"
        }
    )

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_add_portfolio_item(client):

    headers = create_authenticated_user(client)

    response = client.post(
        "/portfolio/",
        headers=headers,
        json={
            "stock_symbol": "IBM",
            "quantity": 5,
            "purchase_price": 200
        }
    )

    assert response.status_code == 201

    body = response.json()

    assert body["success"] is True
    assert body["data"]["stock_symbol"] == "IBM"
    assert body["data"]["quantity"] == 5


def test_invalid_portfolio_quantity(client):

    headers = create_authenticated_user(client)

    response = client.post(
        "/portfolio/",
        headers=headers,
        json={
            "stock_symbol": "IBM",
            "quantity": 0,
            "purchase_price": 200
        }
    )

    assert response.status_code == 400


def test_get_portfolio(client):

    headers = create_authenticated_user(client)

    client.post(
        "/portfolio/",
        headers=headers,
        json={
            "stock_symbol": "IBM",
            "quantity": 5,
            "purchase_price": 200
        }
    )

    response = client.get(
        "/portfolio/",
        headers=headers
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["stock_symbol"] == "IBM"


def test_delete_portfolio_item(client):

    headers = create_authenticated_user(client)

    create_response = client.post(
        "/portfolio/",
        headers=headers,
        json={
            "stock_symbol": "IBM",
            "quantity": 5,
            "purchase_price": 200
        }
    )

    portfolio_id = create_response.json()["data"]["id"]

    delete_response = client.delete(
        f"/portfolio/{portfolio_id}",
        headers=headers
    )

    assert delete_response.status_code == 200

    get_response = client.get(
        "/portfolio/",
        headers=headers
    )

    assert get_response.json()["data"] == []