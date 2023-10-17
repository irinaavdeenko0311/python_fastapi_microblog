from typing import AsyncGenerator, List, Type

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from database import models
from database.config import async_session


async def get_async_session() -> AsyncGenerator:
    """Корутина для создания асинхронного генератора сессии БД."""

    async with async_session.begin() as session:
        try:
            yield session
        except BaseException:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_user_id_from_api_key(api_key: str) -> select:
    """Функция для получения ID пользователя по его api-key"""

    return select(models.UserApiKey.user_id).where(models.UserApiKey.api_key == api_key)


async def get_follows(
    follows_id: List[int], db: AsyncSession = Depends(get_async_session)
) -> List:
    """Корутина для получения списка подписок/подписчиков пользователя."""

    follows_query = await db.execute(
        select(models.User).where(models.User.id.in_(follows_id))
    )
    follows_obj = follows_query.scalars().all()
    return [schemas.UserShort(**jsonable_encoder(follower)) for follower in follows_obj]


async def get_user_info(
    query: select, db: AsyncSession = Depends(get_async_session)
) -> schemas.ResultUser:
    """Корутина для получения полной информации о пользователе."""

    result = await db.execute(query)
    user_obj = result.scalars().first()

    followers_id = [follow.follower_user_id for follow in user_obj.followers]
    followers = await get_follows(followers_id, db)

    followings_id = [follow.following_user_id for follow in user_obj.followings]
    followings = await get_follows(followings_id, db)

    user = schemas.UserFull(
        id=user_obj.id, name=user_obj.name, followers=followers, following=followings
    )
    return schemas.ResultUser(user=user)


class MicroblogException(Exception):

    """Кастомный класс исключений для приложения."""

    def __init__(
        self, status_code: int, error_type: Type[Exception], error_message: str
    ) -> None:
        self.status_code = status_code
        self.error_type = error_type
        self.error_message = error_message
