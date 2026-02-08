"""Репозиторий организаций."""

from sqlalchemy.orm import Session, joinedload

from app.models.building import Building
from app.models.organization import Organization, organization_activities
from app.repositories.base import paginate
from app.utils.geo import bbox_filter, haversine_distance


class OrganizationRepository:
    """Доступ к данным организаций."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, org_id: int) -> Organization | None:
        """Организация со всеми связями (здание, телефоны, активности)."""
        return (
            self.db.query(Organization)
            .options(
                joinedload(Organization.building),
                joinedload(Organization.phones),
                joinedload(Organization.activities),
            )
            .filter(Organization.id == org_id)
            .first()
        )

    def get_by_building_id(
        self, building_id: int, *, limit: int, offset: int
    ) -> tuple[list[Organization], int]:
        """Организации в указанном здании."""
        query = self.db.query(Organization).filter(
            Organization.building_id == building_id
        )
        return paginate(query, limit=limit, offset=offset)

    def get_by_activity_id(
        self, activity_id: int, *, limit: int, offset: int
    ) -> tuple[list[Organization], int]:
        """Организации с конкретной активностью (без учёта дочерних)."""
        query = (
            self.db.query(Organization)
            .join(organization_activities)
            .filter(organization_activities.c.activity_id == activity_id)
        )
        return paginate(query, limit=limit, offset=offset)

    def get_by_activity_ids(
        self, activity_ids: list[int], *, limit: int, offset: int
    ) -> tuple[list[Organization], int]:
        """Организации по списку ID активностей. Дубли исключены через DISTINCT."""
        query = (
            self.db.query(Organization)
            .join(organization_activities)
            .filter(organization_activities.c.activity_id.in_(activity_ids))
            .distinct()
        )
        return paginate(query, limit=limit, offset=offset)

    def search_by_name(
        self, query_str: str, *, limit: int, offset: int
    ) -> tuple[list[Organization], int]:
        """Поиск по частичному совпадению имени (ILIKE)."""
        query = self.db.query(Organization).filter(
            Organization.name.ilike(f"%{query_str}%")
        )
        return paginate(query, limit=limit, offset=offset)

    def search_in_radius(
        self, lat: float, lng: float, radius_meters: float,
        *, limit: int, offset: int,
    ) -> tuple[list[Organization], int]:
        """Поиск в радиусе: bbox-префильтр (по индексу) + точный Haversine."""
        query = (
            self.db.query(Organization)
            .join(Building)
            .filter(bbox_filter(lat, lng, radius_meters))
            .filter(haversine_distance(lat, lng) <= radius_meters)
        )
        return paginate(query, limit=limit, offset=offset)

    def search_in_rectangle(
        self,
        lat_min: float, lat_max: float,
        lng_min: float, lng_max: float,
        *, limit: int, offset: int,
    ) -> tuple[list[Organization], int]:
        """Поиск в прямоугольной области по координатам."""
        query = (
            self.db.query(Organization)
            .join(Building)
            .filter(
                Building.latitude.between(lat_min, lat_max),
                Building.longitude.between(lng_min, lng_max),
            )
        )
        return paginate(query, limit=limit, offset=offset)
