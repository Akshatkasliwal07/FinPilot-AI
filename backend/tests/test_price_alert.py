def create_authenticated_user(client):

    client.post(
        "/users/signup",
        json={
            "name": "Price Alert User",
            "email": "alert@example.com",
            "password": "Test@12345"
        }
    )

    login = client.post(
        "/users/login",
        data={
            "username": "alert@example.com",
            "password": "Test@12345"
        }
    )

    token = login.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_create_price_alert(client):

    headers = create_authenticated_user(client)

    response = client.post(
        "/price-alerts/",
        headers=headers,
        json={
            "stock_symbol": "IBM",
            "target_price": 220,
            "condition": "above"
        }
    )

    assert response.status_code == 201

    body = response.json()

    assert body["success"] is True
    assert body["data"]["stock_symbol"] == "IBM"


def test_get_price_alerts(client):

    headers = create_authenticated_user(client)

    client.post(
        "/price-alerts/",
        headers=headers,
        json={
            "stock_symbol": "IBM",
            "target_price": 220,
            "condition": "above"
        }
    )

    response = client.get(
        "/price-alerts/?page=1&limit=10",
        headers=headers
    )

    assert response.status_code == 200

    body = response.json()

    assert body["data"]["total"] == 1
    assert len(body["data"]["items"]) == 1


def test_filter_price_alerts(client):

    headers = create_authenticated_user(client)

    client.post(
        "/price-alerts/",
        headers=headers,
        json={
            "stock_symbol": "IBM",
            "target_price": 220,
            "condition": "above"
        }
    )

    client.post(
        "/price-alerts/",
        headers=headers,
        json={
            "stock_symbol": "AAPL",
            "target_price": 180,
            "condition": "below"
        }
    )

    response = client.get(
        "/price-alerts/?page=1&limit=10&symbol=IBM",
        headers=headers
    )

    body = response.json()

    assert body["data"]["total"] == 1
    assert body["data"]["items"][0]["stock_symbol"] == "IBM"


def test_delete_price_alert(client):

    headers = create_authenticated_user(client)

    create = client.post(
        "/price-alerts/",
        headers=headers,
        json={
            "stock_symbol": "IBM",
            "target_price": 220,
            "condition": "above"
        }
    )

    alert_id = create.json()["data"]["id"]

    delete = client.delete(
        f"/price-alerts/{alert_id}",
        headers=headers
    )

    assert delete.status_code == 200

    response = client.get(
        "/price-alerts/?page=1&limit=10",
        headers=headers
    )

    assert response.json()["data"]["total"] == 0
    