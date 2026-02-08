"""ORM-модели: регистрация всех таблиц для Alembic и Base.metadata."""

from app.models.building import Building
from app.models.activity import Activity
from app.models.organization import Organization, OrganizationPhone, organization_activities

__all__ = [
    "Building",
    "Activity",
    "Organization",
    "OrganizationPhone",
    "organization_activities",
]
