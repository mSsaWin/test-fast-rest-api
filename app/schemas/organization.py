"""Pydantic-схемы организаций."""

from pydantic import BaseModel, Field

from app.schemas.activity import ActivityRead
from app.schemas.building import BuildingRead


class PhoneRead(BaseModel):
    """Телефон организации."""

    id: int = Field(examples=[1])
    phone_number: str = Field(examples=["2-222-222"])

    model_config = {"from_attributes": True}


class OrganizationRead(BaseModel):
    """Организация — полное представление со связями (detail endpoint)."""

    id: int = Field(examples=[1])
    name: str = Field(examples=['ООО "Рога и Копыта"'])
    building: BuildingRead
    phones: list[PhoneRead]
    activities: list[ActivityRead]

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": 'ООО "Рога и Копыта"',
                    "building": {
                        "id": 1,
                        "address": "г. Москва, ул. Ленина 1, офис 3",
                        "latitude": 55.7558,
                        "longitude": 37.6173,
                    },
                    "phones": [
                        {"id": 1, "phone_number": "2-222-222"},
                        {"id": 2, "phone_number": "3-333-333"},
                    ],
                    "activities": [
                        {"id": 2, "name": "Мясная продукция", "parent_id": 1, "level": 2},
                        {"id": 3, "name": "Молочная продукция", "parent_id": 1, "level": 2},
                    ],
                }
            ]
        },
    }


class OrganizationList(BaseModel):
    """Организация — краткое представление для списков."""

    id: int = Field(examples=[1])
    name: str = Field(examples=['ООО "Рога и Копыта"'])
    building_id: int = Field(examples=[1])

    model_config = {"from_attributes": True}
