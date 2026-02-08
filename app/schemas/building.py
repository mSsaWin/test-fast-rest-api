"""Pydantic-схемы зданий."""

from pydantic import BaseModel, Field


class BuildingRead(BaseModel):
    """Здание — ответ API."""

    id: int = Field(examples=[1])
    address: str = Field(examples=["г. Москва, ул. Ленина 1, офис 3"])
    latitude: float = Field(examples=[55.7558])
    longitude: float = Field(examples=[37.6173])

    model_config = {"from_attributes": True}
