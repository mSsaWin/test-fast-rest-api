"""Эндпоинты организаций: чтение, поиск по имени, активности, геопоиск."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.dependencies import Pagination, get_db, get_pagination
from app.schemas.organization import OrganizationList, OrganizationRead
from app.schemas.pagination import PaginatedResponse
from app.services.organization import OrganizationService
from app.utils.pagination import build_paginated_response

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get(
    "/by-building/{building_id}",
    response_model=PaginatedResponse[OrganizationList],
    summary="Организации в здании",
    description="Возвращает список всех организаций, находящихся в указанном здании.",
)
def get_organizations_by_building(
    building_id: int,
    request: Request,
    pagination: Pagination = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    service = OrganizationService(db)
    items, total = service.get_by_building(
        building_id, limit=pagination.limit, offset=pagination.offset
    )
    return build_paginated_response(items, total, pagination.limit, pagination.offset, request)


@router.get(
    "/by-activity/{activity_id}",
    response_model=PaginatedResponse[OrganizationList],
    summary="Организации по виду деятельности",
    description=(
        "Возвращает список организаций, которые относятся к указанному "
        "виду деятельности (без учёта вложенных)."
    ),
)
def get_organizations_by_activity(
    activity_id: int,
    request: Request,
    pagination: Pagination = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    service = OrganizationService(db)
    items, total = service.get_by_activity(
        activity_id, limit=pagination.limit, offset=pagination.offset
    )
    return build_paginated_response(items, total, pagination.limit, pagination.offset, request)


@router.get(
    "/search/activity/{activity_id}",
    response_model=PaginatedResponse[OrganizationList],
    summary="Поиск организаций по деятельности (с вложенными)",
    description=(
        "Ищет организации по виду деятельности с учётом всех вложенных "
        "подкатегорий. Например, поиск по «Еда» вернёт организации "
        "с деятельностями «Мясная продукция», «Молочная продукция» и т.д."
    ),
)
def search_organizations_by_activity(
    activity_id: int,
    request: Request,
    pagination: Pagination = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    service = OrganizationService(db)
    items, total = service.search_by_activity_recursive(
        activity_id, limit=pagination.limit, offset=pagination.offset
    )
    return build_paginated_response(items, total, pagination.limit, pagination.offset, request)


@router.get(
    "/search/name",
    response_model=PaginatedResponse[OrganizationList],
    summary="Поиск организаций по названию",
    description="Ищет организации по частичному совпадению названия (без учёта регистра).",
)
def search_organizations_by_name(
    request: Request,
    q: str = Query(..., min_length=1, description="Строка для поиска в названии"),
    pagination: Pagination = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    service = OrganizationService(db)
    items, total = service.search_by_name(
        q, limit=pagination.limit, offset=pagination.offset
    )
    return build_paginated_response(items, total, pagination.limit, pagination.offset, request)


@router.get(
    "/search/radius",
    response_model=PaginatedResponse[OrganizationList],
    summary="Поиск организаций в радиусе",
    description="Ищет организации в заданном радиусе от указанной точки (в метрах).",
)
def search_organizations_in_radius(
    request: Request,
    lat: float = Query(..., ge=-90, le=90, description="Широта центра"),
    lng: float = Query(..., ge=-180, le=180, description="Долгота центра"),
    radius: float = Query(..., gt=0, le=40_075_000, description="Радиус поиска в метрах"),
    pagination: Pagination = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    service = OrganizationService(db)
    items, total = service.search_in_radius(
        lat, lng, radius, limit=pagination.limit, offset=pagination.offset
    )
    return build_paginated_response(items, total, pagination.limit, pagination.offset, request)


@router.get(
    "/search/rectangle",
    response_model=PaginatedResponse[OrganizationList],
    summary="Поиск организаций в прямоугольнике",
    description="Ищет организации внутри заданной прямоугольной области по координатам.",
)
def search_organizations_in_rectangle(
    request: Request,
    lat_min: float = Query(..., ge=-90, le=90, description="Мин. широта"),
    lat_max: float = Query(..., ge=-90, le=90, description="Макс. широта"),
    lng_min: float = Query(..., ge=-180, le=180, description="Мин. долгота"),
    lng_max: float = Query(..., ge=-180, le=180, description="Макс. долгота"),
    pagination: Pagination = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    if lat_min >= lat_max:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="lat_min должен быть меньше lat_max",
        )
    if lng_min >= lng_max:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="lng_min должен быть меньше lng_max",
        )
    service = OrganizationService(db)
    items, total = service.search_in_rectangle(
        lat_min, lat_max, lng_min, lng_max,
        limit=pagination.limit, offset=pagination.offset,
    )
    return build_paginated_response(items, total, pagination.limit, pagination.offset, request)


@router.get(
    "/{org_id}",
    response_model=OrganizationRead,
    summary="Информация об организации",
    description="Возвращает полную информацию об организации по её идентификатору.",
)
def get_organization(org_id: int, db: Session = Depends(get_db)):
    service = OrganizationService(db)
    return service.get_by_id(org_id)
