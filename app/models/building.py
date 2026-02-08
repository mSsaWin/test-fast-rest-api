"""Модель здания с адресом и географическими координатами."""

from sqlalchemy import CheckConstraint, Column, DateTime, Float, Index, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class Building(Base):
    """Здание. Содержит адрес, координаты и связь с организациями."""

    __tablename__ = "buildings"
    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="check_latitude_range"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="check_longitude_range"),
        Index("ix_buildings_lat_lng", "latitude", "longitude"),
    )

    id = Column(Integer, primary_key=True)
    address = Column(String(500), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    organizations = relationship("Organization", back_populates="building")
