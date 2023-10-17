from os import environ

import dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

dotenv.load_dotenv()

POSTGRES_USER = environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD")
DB_HOST = environ.get("DB_HOST")
DB_NAME = environ.get("DB_NAME")
DB_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
)

async_engine = create_async_engine(DB_URL, echo=True)
async_session = async_sessionmaker(
    async_engine, expire_on_commit=False, autocommit=False, autoflush=False
)
