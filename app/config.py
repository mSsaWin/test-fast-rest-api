"""Настройки приложения. Значения берутся из переменных окружения / .env файла."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Конфигурация приложения. Все поля переопределяемы через ENV."""

    database_url: str = "postgresql://postgres:postgres@db:5432/directory_db"
    api_key: str = "my-secret-api-key"
    page_size_default: int = 20
    page_size_max: int = 100

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
