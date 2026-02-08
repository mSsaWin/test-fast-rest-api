"""Сервис видов деятельности."""

from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.repositories.activity import ActivityRepository
from app.schemas.activity import ActivityTree


class ActivityService:
    """Бизнес-логика видов деятельности."""

    def __init__(self, db: Session):
        self.repo = ActivityRepository(db)

    def get_tree(self) -> list[ActivityTree]:
        """Дерево активностей — корневые узлы с вложенными children."""
        all_activities = self.repo.get_all()
        return self._build_tree(all_activities)

    def get_descendant_ids(
        self, activity_id: int, *, include_self: bool = True
    ) -> list[int]:
        """ID активности и всех её потомков."""
        return self.repo.get_descendant_ids(activity_id, include_self=include_self)

    def _build_tree(self, activities: list[Activity]) -> list[ActivityTree]:
        """Собрать плоский список в дерево через словарь id→node."""
        activity_map: dict[int, ActivityTree] = {}
        roots: list[ActivityTree] = []

        for act in activities:
            activity_map[act.id] = ActivityTree(
                id=act.id,
                name=act.name,
                level=act.level,
                children=[],
            )

        for act in activities:
            node = activity_map[act.id]
            if act.parent_id is None:
                roots.append(node)
            elif act.parent_id in activity_map:
                activity_map[act.parent_id].children.append(node)

        return roots
