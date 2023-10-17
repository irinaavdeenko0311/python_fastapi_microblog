import os
import sys
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy_utils.functions import drop_database

PARENT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PARENT_DIR)

from common import get_async_session
from database import models
from routes import app as _app
from tests.data_test_db import DATA_TEST_DB

TESTS_DIR = os.path.dirname(__file__)
DB_URL = f"sqlite+aiosqlite:///{TESTS_DIR}/test_microblog.db"

async_engine = create_async_engine(DB_URL, echo=True)
TestingSession = async_sessionmaker(
    async_engine, expire_on_commit=False, autocommit=False, autoflush=False
)


async def override_get_async_session() -> AsyncGenerator:
    """Корутина для создания асинхронного генератора сессии тестовой БД."""

    async with TestingSession.begin() as session:
        try:
            yield session
        except BaseException:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture(autouse=True)
async def create_db() -> AsyncGenerator:
    """Фикстура по созданию и заполнению БД, а также её удалению после тестов."""

    async with async_engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

        async with TestingSession.begin() as session:
            await session.run_sync(
                lambda session: session.bulk_save_objects(DATA_TEST_DB)
            )

    yield

    drop_database(DB_URL)


@pytest.fixture
def app() -> Generator:
    """Фикстура, 'подменяющая' сессию приложения на тестовую."""

    _app.dependency_overrides[get_async_session] = override_get_async_session
    yield _app


@pytest.fixture
def client(app: FastAPI) -> Generator:
    """Фикстура по созданию тестового клиента."""

    client = TestClient(app)
    yield client
