"""Pydantic-схемы видов деятельности."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ActivityRead(BaseModel):
    """Активность — плоское представление."""

    id: int = Field(examples=[3])
    name: str = Field(examples=["Молочная продукция"])
    parent_id: int | None = Field(default=None, examples=[1])
    level: int = Field(examples=[2])

    model_config = {"from_attributes": True}


class ActivityTree(BaseModel):
    """Активность — древовидное представление с вложенными children."""

    id: int = Field(examples=[1])
    name: str = Field(examples=["Еда"])
    level: int = Field(examples=[1])
    children: list[ActivityTree] = []

    model_config = {"from_attributes": True}
