from typing import List

from pydantic import BaseModel, Field

"""Схемы для обработки входных данных от пользователя."""


class TweetIn(BaseModel):
    """Схема для полученного от пользователя твита."""

    content: str = Field(..., max_length=500, validation_alias="tweet_data")
    tweet_media_ids: List[int] = list()


"""Схемы для подготовки выходных данных о пользователе."""


class UserBase(BaseModel):
    """Базовая схема представления данных пользователя."""

    name: str = Field(..., max_length=20)


class UserShort(UserBase):
    """Схема представления данных пользователя в сокращенном виде - id и name."""

    id: int


class UserForLikes(UserBase):
    """
    Схема представления данных пользователя.

    Используется в выводе информации о твите - список лайкнувших пользователей.
    """

    user_id: int = Field(..., validation_alias="id")


class UserFull(UserShort):
    """Схема представления данных пользователя в полном виде."""

    followers: List[UserShort]
    following: List[UserShort]


"""Схемы для подготовки выходных данных о твите."""


class Tweet(BaseModel):
    """Схема для представления полной информации о твите."""

    id: int
    content: str = Field(..., max_length=500)
    attachments: List[str] = Field(
        ..., description="List of paths to files that were attached to the tweet."
    )
    author: UserShort
    likes: List[UserForLikes] = Field(
        ..., description="List of users who liked the tweet."
    )


"""Схемы для подготовки конечного результата."""


class ResultSuccess(BaseModel):
    """Базовая схема для ответа при успешном результате запроса."""

    result: bool = True


class ResultCreateTweet(ResultSuccess):
    """Схема для ответа при создании твита."""

    tweet_id: int


class ResultAddMedia(ResultSuccess):
    """Схема для ответа при добавлении файла."""

    media_id: int


class ResultTweets(ResultSuccess):
    """Схема для ответа при запросе ленты твитов."""

    tweets: List[Tweet]


class ResultUser(ResultSuccess):
    """Схема для удачного ответа на запрос получения информации о пользователе."""

    user: UserFull


class ResultUnsuccess(BaseModel):
    """Базовая схема для ответа при неуспешном результате запроса."""

    result: bool = False
    error_type: str
    error_message: str
