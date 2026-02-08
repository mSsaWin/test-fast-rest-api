"""FastAPI-зависимости: сессия БД, авторизация, параметры пагинации."""

from dataclasses import dataclass

from fastapi import HTTPException, Query, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings
from app.database import SessionLocal

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_db():
    """Сессия БД на время запроса. Закрывается автоматически."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Проверка заголовка X-API-Key. 401 — нет ключа, 403 — неверный."""
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
        )
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return api_key


@dataclass
class Pagination:
    """Параметры пагинации, извлечённые из query-строки."""

    limit: int
    offset: int


def get_pagination(
    limit: int = Query(
        default=settings.page_size_default,
        ge=1,
        le=settings.page_size_max,
        description="Количество элементов на странице",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Смещение от начала списка",
    ),
) -> Pagination:
    """Извлечь и провалидировать limit/offset из query-параметров."""
    return Pagination(limit=limit, offset=offset)
