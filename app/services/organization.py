"""Сервис организаций."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.repositories.activity import ActivityRepository
from app.repositories.organization import OrganizationRepository


class OrganizationService:
    """Бизнес-логика организаций."""

    def __init__(self, db: Session):
        self.repo = OrganizationRepository(db)
        self.activity_repo = ActivityRepository(db)

    def get_by_id(self, org_id: int) -> Organization:
        """Организация по ID. Поднимает 404, если не найдена."""
        org = self.repo.get_by_id(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization with id {org_id} not found",
            )
        return org

    def get_by_building(
        self, building_id: int, *, limit: int, offset: int
    ) -> tuple[list[Organization], int]:
        """Организации в указанном здании."""
        return self.repo.get_by_building_id(building_id, limit=limit, offset=offset)

    def get_by_activity(
        self, activity_id: int, *, limit: int, offset: int
    ) -> tuple[list[Organization], int]:
        """Организации с конкретной активностью (без вложенных)."""
        return self.repo.get_by_activity_id(activity_id, limit=limit, offset=offset)

    def search_by_activity_recursive(
        self, activity_id: int, *, limit: int, offset: int
    ) -> tuple[list[Organization], int]:
        """Поиск по активности с учётом всех дочерних уровней."""
        activity_ids = self.activity_repo.get_descendant_ids(activity_id)
        return self.repo.get_by_activity_ids(activity_ids, limit=limit, offset=offset)

    def search_by_name(
        self, query: str, *, limit: int, offset: int
    ) -> tuple[list[Organization], int]:
        """Поиск по частичному совпадению названия (без учёта регистра)."""
        return self.repo.search_by_name(query, limit=limit, offset=offset)

    def search_in_radius(
        self, lat: float, lng: float, radius: float,
        *, limit: int, offset: int,
    ) -> tuple[list[Organization], int]:
        """Организации в радиусе от точки (метры)."""
        return self.repo.search_in_radius(lat, lng, radius, limit=limit, offset=offset)

    def search_in_rectangle(
        self,
        lat_min: float, lat_max: float,
        lng_min: float, lng_max: float,
        *, limit: int, offset: int,
    ) -> tuple[list[Organization], int]:
        """Организации в прямоугольной области."""
        return self.repo.search_in_rectangle(
            lat_min, lat_max, lng_min, lng_max, limit=limit, offset=offset
        )
