import io
import os
import sys

from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

PARENT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PARENT_DIR)

from schemas import ResultAddMedia, ResultCreateTweet, ResultSuccess


def test_create_tweet(client: TestClient) -> None:
    """Тест по проверке endpoint '/api/tweets', создание нового твита, метод post."""

    body1 = {"tweet_data": "test_content"}
    response = client.post("/api/tweets", json=body1, headers={"api-key": "test"})
    correct_response = jsonable_encoder(ResultCreateTweet(tweet_id=6))
    assert response.json() == correct_response
    assert response.status_code == 201

    body2 = {"tweet_data": "test content", "tweet_media_ids": []}
    response = client.post("/api/tweets", json=body2, headers={"api-key": "test"})
    correct_response = jsonable_encoder(ResultCreateTweet(tweet_id=7))
    assert response.json() == correct_response
    assert response.status_code == 201

    body3 = {"tweet_data": "test content", "tweet_media_ids": [1]}
    response = client.post("/api/tweets", json=body3, headers={"api-key": "test"})
    correct_response = jsonable_encoder(ResultCreateTweet(tweet_id=8))
    assert response.json() == correct_response
    assert response.status_code == 201

    body4 = {"tweet_data": "test content", "tweet_media_ids": [1, 2]}
    response = client.post("/api/tweets", json=body4, headers={"api-key": "test"})
    correct_response = jsonable_encoder(ResultCreateTweet(tweet_id=9))
    assert response.json() == correct_response
    assert response.status_code == 201


def test_add_file_media(client: TestClient) -> None:
    """Тест по проверке endpoint '/api/medias', добавление нового файла, метод post."""

    file = ("test_file", io.BytesIO())
    response = client.post("/api/medias", files={"file": file})
    correct_response = jsonable_encoder(ResultAddMedia(media_id=4))
    assert response.json() == correct_response
    assert response.status_code == 201


def test_delete_tweet(client: TestClient) -> None:
    """Тест по проверке endpoint '/api/tweets/{id}', удаление твита, метод delete."""

    tweet_id = 4
    response = client.delete(f"/api/tweets/{tweet_id}", headers={"api-key": "test"})
    correct_response = jsonable_encoder(ResultSuccess())
    assert response.json() == correct_response
    assert response.status_code == 200


def test_add_like_tweet(client: TestClient) -> None:
    """Тест по проверке endpoint '/api/tweets/{id}/likes', добавление лайка, метод post."""

    tweet_id = 2
    response = client.post(f"/api/tweets/{tweet_id}/likes", headers={"api-key": "test"})
    correct_response = jsonable_encoder(ResultSuccess())
    assert response.json() == correct_response
    assert response.status_code == 201
    client.delete(f"/api/tweets/{tweet_id}/likes")


def test_delete_like_tweet(client: TestClient) -> None:
    """Тест по проверке endpoint '/api/tweets/{id}/likes', удаление лайка, метод delete."""

    tweet_id = 4
    response = client.delete(
        f"/api/tweets/{tweet_id}/likes", headers={"api-key": "test"}
    )
    correct_response = jsonable_encoder(ResultSuccess())
    assert response.json() == correct_response
    assert response.status_code == 200
    client.post(f"/api/tweets/{tweet_id}/likes")


def test_start_following(client: TestClient) -> None:
    """Тест по проверке endpoint '/api/users/{id}/follow', добавление подписки, метод post."""

    user_id = 4
    response = client.post(f"/api/users/{user_id}/follow", headers={"api-key": "test"})
    correct_response = jsonable_encoder(ResultSuccess())
    assert response.json() == correct_response
    assert response.status_code == 201
    client.delete(f"/api/users/{user_id}/follow")


def test_stop_following(client: TestClient) -> None:
    """Тест по проверке endpoint '/api/users/{id}/follow', удаление подписки, метод delete."""

    user_id = 3
    response = client.delete(
        f"/api/users/{user_id}/follow", headers={"api-key": "test"}
    )
    correct_response = jsonable_encoder(ResultSuccess())
    assert response.json() == correct_response
    assert response.status_code == 200
    client.post(f"/api/users/{user_id}/follow")


def test_get_tweet_feed(client: TestClient) -> None:
    """Тест по проверке endpoint '/api/tweets', лента твитов, метод get."""

    response = client.get("/api/tweets", headers={"api-key": "test"})
    correct_response = {
        "result": True,
        "tweets": [
            {
                "id": 4,
                "content": "tweet4",
                "attachments": [],
                "author": {"id": 1, "name": "Irina"},
                "likes": [
                    {"user_id": 1, "name": "Irina"},
                    {"user_id": 2, "name": "Alex"},
                ],
            },
            {
                "id": 3,
                "content": "tweet3",
                "attachments": [],
                "author": {"id": 3, "name": "Olga"},
                "likes": [{"user_id": 1, "name": "Irina"}],
            },
            {
                "id": 2,
                "content": "tweet2",
                "attachments": ["link3"],
                "author": {"id": 3, "name": "Olga"},
                "likes": [{"user_id": 3, "name": "Olga"}],
            },
            {
                "id": 1,
                "content": "tweet1",
                "attachments": ["link1", "link2"],
                "author": {"id": 2, "name": "Alex"},
                "likes": [{"user_id": 2, "name": "Alex"}],
            },
        ],
    }
    assert response.json() == correct_response
    assert response.status_code == 200


def test_get_user_info_about_self(client: TestClient) -> None:
    """Тест по проверке endpoint '/api/users/me', информация о себе, метод get."""

    response = client.get("/api/users/me", headers={"api-key": "test"})
    correct_response = {
        "result": True,
        "user": {
            "id": 1,
            "name": "Irina",
            "followers": [{"id": 2, "name": "Alex"}, {"id": 4, "name": "John"}],
            "following": [{"id": 2, "name": "Alex"}, {"id": 3, "name": "Olga"}],
        },
    }
    assert response.json() == correct_response
    assert response.status_code == 200


def test_get_user_info_about_another(client: TestClient) -> None:
    """Тест по проверке endpoint '/api/users/me', информация о пользователе, метод get."""

    user_id = 2
    response = client.get(f"/api/users/{user_id}", headers={"api-key": "test"})
    correct_response = {
        "result": True,
        "user": {
            "id": 2,
            "name": "Alex",
            "followers": [{"id": 1, "name": "Irina"}, {"id": 3, "name": "Olga"}],
            "following": [{"id": 1, "name": "Irina"}, {"id": 3, "name": "Olga"}],
        },
    }
    assert response.json() == correct_response
    assert response.status_code == 200
