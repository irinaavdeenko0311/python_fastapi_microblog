import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    APP_NAME: str = "microblog"
    TESTING: bool = False
    APP_DIR: str = os.path.dirname(__file__)
    STATIC_DIR: str = os.path.join(APP_DIR, "static")
    MEDIA_DIR: str = os.path.join(STATIC_DIR, "images")
    STATIC_PATH: str = "/static"
    MEDIA_PATH: str = os.path.join(STATIC_PATH, "images")
    LOGGING_CONFIG_PATH: str = os.path.join(APP_DIR, "logging/logging_config.ini")


settings = Settings()
