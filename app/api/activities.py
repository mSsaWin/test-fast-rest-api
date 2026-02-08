"""Эндпоинты видов деятельности."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.activity import ActivityTree
from app.services.activity import ActivityService

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get(
    "/",
    response_model=list[ActivityTree],
    summary="Дерево деятельностей",
    description=(
        "Возвращает все виды деятельности в древовидной структуре. "
        "Максимальная вложенность — 3 уровня."
    ),
)
def get_activities(db: Session = Depends(get_db)):
    service = ActivityService(db)
    return service.get_tree()
