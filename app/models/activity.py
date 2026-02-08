"""Модель вида деятельности с иерархией до 3 уровней."""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Activity(Base):
    """Вид деятельности. Дерево parent→children, глубина ограничена level 1–3."""

    __tablename__ = "activities"
    __table_args__ = (
        CheckConstraint("level >= 1 AND level <= 3", name="check_activity_level"),
        CheckConstraint(
            "(parent_id IS NULL AND level = 1) OR (parent_id IS NOT NULL AND level > 1)",
            name="check_activity_root_level",
        ),
        UniqueConstraint("name", "parent_id", name="uq_activity_name_parent"),
        Index("ix_activities_parent_id", "parent_id"),
        Index("ix_activities_parent_level", "parent_id", "level"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    level = Column(Integer, nullable=False, default=1)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    parent = relationship("Activity", remote_side=[id], back_populates="children")
    children = relationship("Activity", back_populates="parent")
    organizations = relationship(
        "Organization",
        secondary="organization_activities",
        back_populates="activities",
    )
