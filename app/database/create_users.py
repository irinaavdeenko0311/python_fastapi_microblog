import asyncio

from sqlalchemy import select

from config import async_session
from models import Follow, User, UserApiKey

users = [User(name=name) for name in ("Irina", "Alex", "Olga", "John")]

api_keys = [
    UserApiKey(api_key="test", user_id=1),
    UserApiKey(api_key="test2", user_id=2),
    UserApiKey(api_key="test3", user_id=3),
    UserApiKey(api_key="test4", user_id=4),
]

follows = [
    Follow(follower_user_id=1, following_user_id=2),
    Follow(follower_user_id=1, following_user_id=3),
    Follow(follower_user_id=2, following_user_id=1),
    Follow(follower_user_id=2, following_user_id=3),
    Follow(follower_user_id=3, following_user_id=1),
    Follow(follower_user_id=3, following_user_id=4),
    Follow(follower_user_id=4, following_user_id=1),
    Follow(follower_user_id=4, following_user_id=2),
    Follow(follower_user_id=4, following_user_id=3),
]


async def create_test_users() -> None:
    """Корутина для создания пользователей."""

    async with async_session.begin() as session:
        response = await session.execute(
            select(UserApiKey).where(UserApiKey.api_key == "test")
        )
        if not response.scalars().first():
            await session.run_sync(lambda session: session.bulk_save_objects(users))
            await session.run_sync(
                lambda session: session.bulk_save_objects(api_keys + follows)
            )


if __name__ == "__main__":
    asyncio.run(create_test_users())
