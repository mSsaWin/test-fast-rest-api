"""Формирование пагинированного ответа в DRF-стиле (count, next, previous, results)."""

from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from fastapi import Request

from app.schemas.pagination import PaginatedResponse


def _build_url(base_url: str, limit: int, offset: int) -> str:
    """Подставить limit/offset в URL, сохранив остальные query-параметры."""
    parsed = urlparse(base_url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params["limit"] = [str(limit)]
    params["offset"] = [str(offset)]
    flat = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
    new_query = urlencode(flat, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def build_paginated_response(
    items: list,
    total: int,
    limit: int,
    offset: int,
    request: Request,
) -> PaginatedResponse:
    """Собрать ответ с next/previous URL на основе текущего request.url."""
    url = str(request.url)

    next_offset = offset + limit
    next_url = (
        _build_url(url, limit, next_offset)
        if next_offset < total
        else None
    )

    prev_offset = offset - limit
    previous_url = (
        _build_url(url, limit, max(prev_offset, 0))
        if offset > 0
        else None
    )

    return PaginatedResponse(
        count=total,
        next=next_url,
        previous=previous_url,
        results=items,
    )
