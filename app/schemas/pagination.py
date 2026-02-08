"""Обёртка пагинации в DRF-стиле: count, next, previous, results."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Пагинированный ответ. next/previous — URL следующей/предыдущей страницы."""

    count: int = Field(examples=[42])
    next: str | None = Field(default=None, examples=["http://localhost:8000/api/v1/buildings/?limit=20&offset=20"])
    previous: str | None = Field(default=None, examples=[None])
    results: list[T]
