"""Репозиторий видов деятельности."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity


class ActivityRepository:
    """Доступ к данным видов деятельности."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Activity]:
        """Все активности (плоский список)."""
        return self.db.query(Activity).all()

    def get_by_id(self, activity_id: int) -> Activity | None:
        """Активность по ID или None."""
        return self.db.query(Activity).filter(Activity.id == activity_id).first()

    def get_root_activities(self) -> list[Activity]:
        """Корневые активности (level 1, без родителя)."""
        return self.db.query(Activity).filter(Activity.parent_id.is_(None)).all()

    def get_descendant_ids(
        self, activity_id: int, *, include_self: bool = True
    ) -> list[int]:
        """ID потомков активности. Глубина дерева <= 3, рекурсия не нужна."""
        activity = self.get_by_id(activity_id)
        if activity is None:
            return []

        result: list[int] = [activity_id] if include_self else []

        if activity.level >= 3:
            return result

        child_ids: list[int] = list(
            self.db.scalars(
                select(Activity.id).where(Activity.parent_id == activity_id)
            ).all()
        )
        result.extend(child_ids)

        if activity.level == 1 and child_ids:
            grandchild_ids = list(
                self.db.scalars(
                    select(Activity.id).where(Activity.parent_id.in_(child_ids))
                ).all()
            )
            result.extend(grandchild_ids)

        return result
