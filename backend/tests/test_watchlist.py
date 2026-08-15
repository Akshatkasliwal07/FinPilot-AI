def create_authenticated_user(client):

    client.post(
        "/users/signup",
        json={
            "name": "Watchlist Test User",
            "email": "watchlist@example.com",
            "password": "Test@12345"
        }
    )

    login_response = client.post(
        "/users/login",
        data={
            "username": "watchlist@example.com",
            "password": "Test@12345"
        }
    )

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_add_watchlist_item(client):

    headers = create_authenticated_user(client)

    response = client.post(
        "/watchlist/",
        headers=headers,
        json={
            "stock_symbol": "IBM"
        }
    )

    assert response.status_code == 201

    body = response.json()

    assert body["success"] is True
    assert body["data"]["stock_symbol"] == "IBM"


def test_duplicate_watchlist_item(client):

    headers = create_authenticated_user(client)

    payload = {
        "stock_symbol": "IBM"
    }

    first_response = client.post(
        "/watchlist/",
        headers=headers,
        json=payload
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/watchlist/",
        headers=headers,
        json=payload
    )

    assert second_response.status_code == 400


def test_get_watchlist_with_pagination(client):

    headers = create_authenticated_user(client)

    client.post(
        "/watchlist/",
        headers=headers,
        json={
            "stock_symbol": "IBM"
        }
    )

    response = client.get(
        "/watchlist/?page=1&limit=10",
        headers=headers
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"]["total"] == 1
    assert body["data"]["page"] == 1
    assert body["data"]["limit"] == 10
    assert len(body["data"]["items"]) == 1


def test_filter_watchlist_by_symbol(client):

    headers = create_authenticated_user(client)

    client.post(
        "/watchlist/",
        headers=headers,
        json={
            "stock_symbol": "IBM"
        }
    )

    client.post(
        "/watchlist/",
        headers=headers,
        json={
            "stock_symbol": "AAPL"
        }
    )

    response = client.get(
        "/watchlist/?page=1&limit=10&symbol=IBM",
        headers=headers
    )

    assert response.status_code == 200

    body = response.json()

    assert body["data"]["total"] == 1
    assert body["data"]["items"][0][
        "stock_symbol"
    ] == "IBM"


def test_delete_watchlist_item(client):

    headers = create_authenticated_user(client)

    create_response = client.post(
        "/watchlist/",
        headers=headers,
        json={
            "stock_symbol": "IBM"
        }
    )

    watchlist_id = create_response.json()["data"]["id"]

    delete_response = client.delete(
        f"/watchlist/{watchlist_id}",
        headers=headers
    )

    assert delete_response.status_code == 200

    get_response = client.get(
        "/watchlist/?page=1&limit=10",
        headers=headers
    )

    body = get_response.json()

    assert body["data"]["total"] == 0
    assert body["data"]["items"] == []
    