"""Репозиторий зданий."""

from sqlalchemy.orm import Session

from app.models.building import Building
from app.repositories.base import paginate


class BuildingRepository:
    """Доступ к данным зданий."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self, *, limit: int, offset: int
    ) -> tuple[list[Building], int]:
        """Все здания с пагинацией."""
        return paginate(self.db.query(Building), limit=limit, offset=offset)

    def get_by_id(self, building_id: int) -> Building | None:
        """Здание по ID или None."""
        return self.db.query(Building).filter(Building.id == building_id).first()
