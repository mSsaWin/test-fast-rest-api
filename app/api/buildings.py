"""Эндпоинты зданий."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.dependencies import Pagination, get_db, get_pagination
from app.schemas.building import BuildingRead
from app.schemas.pagination import PaginatedResponse
from app.services.building import BuildingService
from app.utils.pagination import build_paginated_response

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get(
    "/",
    response_model=PaginatedResponse[BuildingRead],
    summary="Список всех зданий",
    description="Возвращает список всех зданий справочника с адресами и координатами.",
)
def get_buildings(
    request: Request,
    pagination: Pagination = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    service = BuildingService(db)
    items, total = service.get_all(limit=pagination.limit, offset=pagination.offset)
    return build_paginated_response(items, total, pagination.limit, pagination.offset, request)
