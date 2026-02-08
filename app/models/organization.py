"""Модели организации, телефонов и связующей таблицы организация↔активность."""

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Table, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.database import Base

organization_activities = Table(
    "organization_activities",
    Base.metadata,
    Column(
        "organization_id",
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "activity_id",
        Integer,
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Index("ix_org_activities_activity_id", "activity_id"),
)
"""Связующая таблица M2M: организация ↔ вид деятельности. Составной PK."""


class Organization(Base):
    """Организация. Привязана к зданию, имеет телефоны и виды деятельности."""

    __tablename__ = "organizations"
    __table_args__ = (
        Index("ix_organizations_building_id", "building_id"),
        Index("ix_organizations_name", "name"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    building = relationship("Building", back_populates="organizations")
    phones = relationship(
        "OrganizationPhone",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    activities = relationship(
        "Activity",
        secondary=organization_activities,
        back_populates="organizations",
    )


class OrganizationPhone(Base):
    """Телефонный номер организации. У одной организации может быть несколько."""

    __tablename__ = "organization_phones"
    __table_args__ = (
        UniqueConstraint("phone_number", name="uq_phone_number"),
        Index("ix_org_phones_organization_id", "organization_id"),
    )

    id = Column(Integer, primary_key=True)
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    phone_number = Column(String(20), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    organization = relationship("Organization", back_populates="phones")
