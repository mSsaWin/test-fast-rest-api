"""Геоутилиты: bounding box, Haversine-выражение для SQLAlchemy."""

import math

from sqlalchemy import and_, func, or_
from sqlalchemy.sql.elements import BooleanClauseList, ColumnElement

from app.models.building import Building

EARTH_RADIUS_METERS = 6_371_000


def build_bbox(
    lat: float, lng: float, radius_meters: float
) -> tuple[float, float, float, float]:
    """Ограничивающий прямоугольник вокруг точки. Учитывает полюса и антимеридиан."""
    delta_lat = math.degrees(radius_meters / EARTH_RADIUS_METERS)

    cos_lat = math.cos(math.radians(lat))
    if cos_lat < 1e-10:
        return (
            max(lat - delta_lat, -90.0),
            min(lat + delta_lat, 90.0),
            -180.0,
            180.0,
        )

    delta_lng = math.degrees(radius_meters / (EARTH_RADIUS_METERS * cos_lat))

    lat_min = max(lat - delta_lat, -90.0)
    lat_max = min(lat + delta_lat, 90.0)
    lng_min = lng - delta_lng
    lng_max = lng + delta_lng

    if lng_min < -180.0:
        lng_min += 360.0
    if lng_max > 180.0:
        lng_max -= 360.0

    return lat_min, lat_max, lng_min, lng_max


def bbox_filter(lat: float, lng: float, radius_meters: float) -> BooleanClauseList:
    """WHERE-условие для bbox-фильтра. При пересечении антимеридиана — OR по долготе."""
    lat_min, lat_max, lng_min, lng_max = build_bbox(lat, lng, radius_meters)

    lat_cond = Building.latitude.between(lat_min, lat_max)

    if lng_min <= lng_max:
        lng_cond = Building.longitude.between(lng_min, lng_max)
    else:
        lng_cond = or_(
            Building.longitude >= lng_min,
            Building.longitude <= lng_max,
        )

    return and_(lat_cond, lng_cond)


def haversine_distance(lat: float, lng: float) -> ColumnElement[float]:
    """SQL-выражение: расстояние Haversine (метры) от точки до Building.(lat, lng)."""
    lat_rad = func.radians(Building.latitude)
    lng_rad = func.radians(Building.longitude)
    point_lat_rad = func.radians(lat)
    point_lng_rad = func.radians(lng)

    dlat = lat_rad - point_lat_rad
    dlng = lng_rad - point_lng_rad

    a = (
        func.power(func.sin(dlat / 2), 2)
        + func.cos(point_lat_rad)
        * func.cos(lat_rad)
        * func.power(func.sin(dlng / 2), 2)
    )
    return EARTH_RADIUS_METERS * 2 * func.asin(func.sqrt(a))
