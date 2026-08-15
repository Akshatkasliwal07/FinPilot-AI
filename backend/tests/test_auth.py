def test_signup_success(client):

    response = client.post(
        "/users/signup",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "Test@12345"
        }
    )

    assert response.status_code == 201

    body = response.json()

    assert body["success"] is True
    assert body["data"]["email"] == "test@example.com"


def test_duplicate_signup(client):

    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "Test@12345"
    }

    first_response = client.post(
        "/users/signup",
        json=payload
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/users/signup",
        json=payload
    )

    assert second_response.status_code == 400


def test_login_success(client):

    client.post(
        "/users/signup",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "Test@12345"
        }
    )

    response = client.post(
        "/users/login",
        data={
            "username": "test@example.com",
            "password": "Test@12345"
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_get_current_user(client):

    client.post(
        "/users/signup",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "Test@12345"
        }
    )

    login_response = client.post(
        "/users/login",
        data={
            "username": "test@example.com",
            "password": "Test@12345"
        }
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"]["email"] == "test@example.com"
    