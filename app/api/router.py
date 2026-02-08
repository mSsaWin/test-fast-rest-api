"""Корневой роутер /api/v1 с авторизацией по API-ключу."""

from fastapi import APIRouter, Depends

from app.api.activities import router as activities_router
from app.api.buildings import router as buildings_router
from app.api.organizations import router as organizations_router
from app.dependencies import verify_api_key

api_router = APIRouter(
    prefix="/api/v1",
    dependencies=[Depends(verify_api_key)],
)

api_router.include_router(organizations_router)
api_router.include_router(buildings_router)
api_router.include_router(activities_router)
