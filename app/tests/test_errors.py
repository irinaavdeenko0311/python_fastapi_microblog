from fastapi.testclient import TestClient


def test_validation_create_tweet(client: TestClient) -> None:
    """Тест по проверке валидации endpoint '/api/tweets', метод post."""

    body1 = {"tweet_data": "t" * 501}
    response = client.post("/api/tweets", json=body1, headers={"api-key": "test"})
    assert response.json()["detail"][0]["type"] == "string_too_long"
    assert response.status_code == 422

    body2 = {"tweet_data": 1}
    response = client.post("/api/tweets", json=body2, headers={"api-key": "test"})
    assert response.json()["detail"][0]["type"] == "string_type"
    assert response.status_code == 422

    body3 = {"tweet_data": "test tweet", "tweet_media_ids": ""}
    response = client.post("/api/tweets", json=body3, headers={"api-key": "test"})
    assert response.json()["detail"][0]["type"] == "list_type"
    assert response.status_code == 422

    body4 = {"tweet_data": "test tweet", "tweet_media_ids": ["a", "b"]}
    response = client.post("/api/tweets", json=body4, headers={"api-key": "test"})
    assert response.json()["detail"][0]["type"] == "int_parsing"
    assert response.status_code == 422


def test_validation_add_file_media(client: TestClient) -> None:
    """Тест по проверке валидации endpoint '/api/medias', метод post."""

    response = client.post("/api/medias")
    assert response.json()["detail"][0]["type"] == "missing"
    assert response.status_code == 422


def test_errors_delete_tweet(client: TestClient) -> None:
    """Тест по проверке ошибок endpoint '/api/tweets/{id}', метод delete."""

    tweet_id = 100
    response = client.delete(f"/api/tweets/{tweet_id}", headers={"api-key": "test"})
    assert response.json() == {
        "result": False,
        "error_type": "ValueError",
        "error_message": "No such tweet",
    }
    assert response.status_code == 404

    tweet_id = 1
    response = client.delete(f"/api/tweets/{tweet_id}", headers={"api-key": "test"})
    assert response.json() == {
        "result": False,
        "error_type": "PermissionError",
        "error_message": "You are not author of the tweet",
    }
    assert response.status_code == 403


def test_errors_add_like_tweet(client: TestClient) -> None:
    """Тест по проверке ошибок endpoint '/api/tweets/{id}/likes', метод post."""

    tweet_id = 100
    response = client.post(f"/api/tweets/{tweet_id}/likes", headers={"api-key": "test"})
    assert response.json() == {
        "result": False,
        "error_type": "ValueError",
        "error_message": "No such tweet",
    }
    assert response.status_code == 404

    tweet_id = 4
    response = client.post(f"/api/tweets/{tweet_id}/likes", headers={"api-key": "test"})
    assert response.json() == {
        "result": False,
        "error_type": "IntegrityError",
        "error_message": "You already liked this tweet",
    }
    assert response.status_code == 400


def test_errors_delete_like_tweet(client: TestClient) -> None:
    """Тест по проверке ошибок endpoint '/api/tweets/{id}/likes', метод delete."""

    tweet_id = 100
    response = client.delete(
        f"/api/tweets/{tweet_id}/likes", headers={"api-key": "test"}
    )
    assert response.json() == {
        "result": False,
        "error_type": "ValueError",
        "error_message": "No such tweet",
    }
    assert response.status_code == 404

    tweet_id = 2
    response = client.delete(
        f"/api/tweets/{tweet_id}/likes", headers={"api-key": "test"}
    )
    assert response.json() == {
        "result": False,
        "error_type": "IntegrityError",
        "error_message": "You didn't like this tweet",
    }
    assert response.status_code == 400


def test_errors_start_following(client: TestClient) -> None:
    """Тест по проверке ошибок endpoint '/api/users/{id}/follow', метод post."""

    user_id = 100
    response = client.post(f"/api/users/{user_id}/follow", headers={"api-key": "test"})
    assert response.json() == {
        "result": False,
        "error_type": "ValueError",
        "error_message": "No such user",
    }
    assert response.status_code == 404

    user_id = 3
    response = client.post(f"/api/users/{user_id}/follow", headers={"api-key": "test"})
    assert response.json() == {
        "result": False,
        "error_type": "IntegrityError",
        "error_message": "You already follower this user",
    }
    assert response.status_code == 400


def test_errors_stop_following(client: TestClient) -> None:
    """Тест по проверке ошибок endpoint '/api/users/{id}/follow', метод delete."""

    user_id = 100
    response = client.delete(
        f"/api/users/{user_id}/follow", headers={"api-key": "test"}
    )
    assert response.json() == {
        "result": False,
        "error_type": "ValueError",
        "error_message": "No such user",
    }
    assert response.status_code == 404

    user_id = 4
    response = client.delete(
        f"/api/users/{user_id}/follow", headers={"api-key": "test"}
    )
    assert response.json() == {
        "result": False,
        "error_type": "IntegrityError",
        "error_message": "You didn't followers this user",
    }
    assert response.status_code == 400


def test_errors_get_user_info_about_another(client: TestClient) -> None:
    """Тест по проверке ошибок endpoint '/api/users/me', метод get."""

    user_id = 100
    response = client.get(f"/api/users/{user_id}", headers={"api-key": "test"})
    assert response.json() == {
        "result": False,
        "error_type": "ValueError",
        "error_message": "No such user",
    }
    assert response.status_code == 404
