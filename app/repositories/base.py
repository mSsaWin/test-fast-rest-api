"""Общие утилиты репозиториев."""

from sqlalchemy.orm import Query


def paginate(query: Query, *, limit: int, offset: int) -> tuple[list, int]:
    """Применить пагинацию к запросу. Возвращает (элементы, общее_количество)."""
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return items, total
