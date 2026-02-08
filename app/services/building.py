"""Сервис зданий."""

from sqlalchemy.orm import Session

from app.models.building import Building
from app.repositories.building import BuildingRepository


class BuildingService:
    """Бизнес-логика зданий."""

    def __init__(self, db: Session):
        self.repo = BuildingRepository(db)

    def get_all(
        self, *, limit: int, offset: int
    ) -> tuple[list[Building], int]:
        """Все здания с пагинацией."""
        return self.repo.get_all(limit=limit, offset=offset)
