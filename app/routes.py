import os
from datetime import datetime

import aiofiles
from fastapi import Depends, FastAPI, File, Header, Path, Request, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import and_, delete, insert, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from common import (
    MicroblogException,
    get_async_session,
    get_user_id_from_api_key,
    get_user_info,
)
from config import settings
from database import models

app = FastAPI(title=settings.APP_NAME, description="Twitter-clone")
app.mount(
    settings.STATIC_PATH, StaticFiles(directory=settings.STATIC_DIR), name="static"
)


@app.post("/api/tweets", response_model=schemas.ResultCreateTweet, status_code=201)
async def create_tweet(
    body: schemas.TweetIn,
    api_key: str = Header(alias="api-key"),
    db: AsyncSession = Depends(get_async_session),
) -> schemas.ResultCreateTweet:
    """Endpoint для получения и сохранения твита."""

    query = (
        insert(models.Tweet)
        .values(
            content=body.content,
            date_time=datetime.now(),
            author_id=(get_user_id_from_api_key(api_key)).scalar_subquery(),  # type: ignore
        )
        .returning(models.Tweet.id)
    )
    result = await db.execute(query)
    tweet_id = result.scalars().first()

    if body.tweet_media_ids:
        await db.execute(
            update(models.Attachment)
            .where(models.Attachment.id.in_(body.tweet_media_ids))
            .values(tweet_id=tweet_id)
        )

    await db.commit()
    return schemas.ResultCreateTweet(tweet_id=tweet_id)


@app.post("/api/medias", response_model=schemas.ResultAddMedia, status_code=201)
async def add_file_media(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_async_session)
) -> schemas.ResultAddMedia:
    """Endpoint для получения файла и добавления его в БД."""

    filename = str(file.filename)
    link = os.path.join(settings.MEDIA_DIR, filename)
    path = os.path.join(settings.MEDIA_PATH, filename)

    async with aiofiles.open(link, "wb") as async_file:
        content = await file.read()
        await async_file.write(content)

    query = insert(models.Attachment).values(link=path).returning(models.Attachment.id)
    result = await db.execute(query)
    media_id = result.scalars().first()

    await db.commit()

    return schemas.ResultAddMedia(media_id=media_id)


@app.delete(
    "/api/tweets/{id}",
    response_model=schemas.ResultSuccess,
    status_code=200,
    responses={
        403: {"model": schemas.ResultUnsuccess},
        404: {"model": schemas.ResultUnsuccess},
    },
)
async def delete_tweet(
    api_key: str = Header(alias="api-key"),
    id: int = Path(...),
    db: AsyncSession = Depends(get_async_session),
) -> schemas.ResultSuccess:
    """Endpoint для удаления твита."""

    response = await db.execute(select(models.Tweet).where(models.Tweet.id == id))
    if not response.scalars().first():
        raise MicroblogException(
            status_code=404, error_type=ValueError, error_message="No such tweet"
        )

    query = (
        delete(models.Tweet)
        .where(
            and_(
                models.Tweet.id == id,
                models.Tweet.author_id
                == (get_user_id_from_api_key(api_key)).scalar_subquery(),  # type: ignore
            )
        )
        .returning(models.Tweet.id)
    )
    response = await db.execute(query)
    result = response.scalars().all()

    if not result:
        raise MicroblogException(
            status_code=403,
            error_type=PermissionError,
            error_message="You are not author of the tweet",
        )

    await db.commit()

    return schemas.ResultSuccess()


@app.post(
    "/api/tweets/{id}/likes",
    response_model=schemas.ResultSuccess,
    status_code=201,
    responses={
        400: {"model": schemas.ResultUnsuccess},
        404: {"model": schemas.ResultUnsuccess},
    },
)
async def add_like_tweet(
    api_key: str = Header(alias="api-key"),
    id: int = Path(...),
    db: AsyncSession = Depends(get_async_session),
) -> schemas.ResultSuccess:
    """Endpoint для проставления лайка на твит."""

    response = await db.execute(select(models.Tweet).where(models.Tweet.id == id))
    if not response.scalars().first():
        raise MicroblogException(
            status_code=404, error_type=ValueError, error_message="No such tweet"
        )

    query = insert(models.Like).values(
        tweet_id=id, user_id=(get_user_id_from_api_key(api_key).scalar_subquery())  # type: ignore
    )
    try:
        await db.execute(query)
        await db.commit()
        return schemas.ResultSuccess()

    except IntegrityError:
        raise MicroblogException(
            status_code=400,
            error_type=IntegrityError,
            error_message="You already liked this tweet",
        )


@app.delete(
    "/api/tweets/{id}/likes",
    response_model=schemas.ResultSuccess,
    status_code=200,
    responses={
        400: {"model": schemas.ResultUnsuccess},
        404: {"model": schemas.ResultUnsuccess},
    },
)
async def delete_like_tweet(
    api_key: str = Header(alias="api-key"),
    id: int = Path(...),
    db: AsyncSession = Depends(get_async_session),
) -> schemas.ResultSuccess:
    """Endpoint для снятия лайка с твита."""

    response = await db.execute(select(models.Tweet).where(models.Tweet.id == id))
    if not response.scalars().first():
        raise MicroblogException(
            status_code=404, error_type=ValueError, error_message="No such tweet"
        )

    query = (
        delete(models.Like)
        .where(
            and_(
                models.Like.tweet_id == id,
                models.Like.user_id
                == (get_user_id_from_api_key(api_key)).scalar_subquery(),  # type: ignore
            )
        )
        .returning(models.Like.tweet_id)
    )
    response = await db.execute(query)
    result = response.scalars().all()

    if not result:
        raise MicroblogException(
            status_code=400,
            error_type=IntegrityError,
            error_message="You didn't like this tweet",
        )

    await db.commit()

    return schemas.ResultSuccess()


@app.post(
    "/api/users/{id}/follow",
    response_model=schemas.ResultSuccess,
    status_code=201,
    responses={
        400: {"model": schemas.ResultUnsuccess},
        404: {"model": schemas.ResultUnsuccess},
    },
)
async def start_following(
    api_key: str = Header(alias="api-key"),
    id: int = Path(...),
    db: AsyncSession = Depends(get_async_session),
) -> schemas.ResultSuccess:
    """Endpoint для подписки на другого пользователя."""

    response = await db.execute(select(models.User).where(models.User.id == id))
    if not response.scalars().first():
        raise MicroblogException(
            status_code=404, error_type=ValueError, error_message="No such user"
        )

    query = insert(models.Follow).values(
        follower_user_id=(get_user_id_from_api_key(api_key).scalar_subquery()),  # type: ignore
        following_user_id=id,
    )

    try:
        await db.execute(query)
        await db.commit()
        return schemas.ResultSuccess()

    except IntegrityError:
        raise MicroblogException(
            status_code=400,
            error_type=IntegrityError,
            error_message="You already follower this user",
        )


@app.delete(
    "/api/users/{id}/follow",
    response_model=schemas.ResultSuccess,
    status_code=200,
    responses={
        400: {"model": schemas.ResultUnsuccess},
        404: {"model": schemas.ResultUnsuccess},
    },
)
async def stop_following(
    api_key: str = Header(alias="api-key"),
    id: int = Path(...),
    db: AsyncSession = Depends(get_async_session),
) -> schemas.ResultSuccess:
    """Endpoint для отписки от другого пользователя."""

    response = await db.execute(select(models.User).where(models.User.id == id))
    if not response.scalars().first():
        raise MicroblogException(
            status_code=404, error_type=ValueError, error_message="No such user"
        )

    query = (
        delete(models.Follow)
        .where(
            and_(
                models.Follow.follower_user_id
                == (get_user_id_from_api_key(api_key)).scalar_subquery(),  # type: ignore
                models.Follow.following_user_id == id,
            )
        )
        .returning(models.Follow.following_user_id)
    )
    response = await db.execute(query)
    result = response.scalars().all()

    if not result:
        raise MicroblogException(
            status_code=400,
            error_type=IntegrityError,
            error_message="You didn't followers this user",
        )

    await db.commit()

    return schemas.ResultSuccess()


@app.get("/api/tweets", response_model=schemas.ResultTweets, status_code=200)
async def get_tweet_feed(
    api_key: str = Header(alias="api-key"),
    db: AsyncSession = Depends(get_async_session),
) -> schemas.ResultTweets:
    """Endpoint для получения ленты с твитами."""
    query = (
        select(models.Tweet)
        .where(
            or_(
                models.Tweet.author_id.in_(
                    select(models.Follow.following_user_id).where(
                        models.Follow.follower_user_id
                        == (get_user_id_from_api_key(api_key)).scalar_subquery()  # type: ignore
                    )
                ),
                models.Tweet.author_id
                == (get_user_id_from_api_key(api_key)).scalar_subquery(),  # type: ignore
            )
        )
        .order_by(models.Tweet.date_time.desc())
    )
    result = await db.execute(query)
    tweets = result.scalars().all()

    tweets = [
        schemas.Tweet(
            id=tweet.id,
            content=tweet.content,
            attachments=[attachment.link for attachment in tweet.attachments],
            author=schemas.UserShort(**jsonable_encoder(tweet.author)),
            likes=[
                schemas.UserForLikes(**jsonable_encoder(like.user))
                for like in tweet.likes
            ],
        )
        for tweet in tweets
    ]

    return schemas.ResultTweets(tweets=tweets)


@app.get("/api/users/me", response_model=schemas.ResultUser, status_code=200)
async def get_user_info_about_self(
    api_key: str = Header(alias="api-key"),
    db: AsyncSession = Depends(get_async_session),
):
    """Endpoint для получения информации о своём профиле."""

    query = select(models.User).where(
        models.User.id == (get_user_id_from_api_key(api_key)).scalar_subquery()  # type: ignore
    )
    return await get_user_info(query, db)


@app.get(
    "/api/users/{id}",
    response_model=schemas.ResultUser,
    status_code=200,
    responses={404: {"model": schemas.ResultUnsuccess}},
)
async def get_user_info_about_another(
    id: int = Path(...), db: AsyncSession = Depends(get_async_session)
):
    """Endpoint для получения информации о профиле другого пользователя."""

    try:
        query = select(models.User).where(models.User.id == id)
        return await get_user_info(query, db)
    except AttributeError:
        raise MicroblogException(
            status_code=404, error_type=ValueError, error_message="No such user"
        )


@app.exception_handler(MicroblogException)
async def all_error(request: Request, exc: MicroblogException) -> JSONResponse:
    """Обработчик исключений."""

    return JSONResponse(
        content={
            "result": False,
            "error_type": exc.error_type.__name__,
            "error_message": exc.error_message,
        },
        status_code=exc.status_code,
    )
