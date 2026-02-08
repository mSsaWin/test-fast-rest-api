"""Точка входа FastAPI-приложения."""

from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(
    title="Organization Directory API",
    description=(
        "REST API приложение для справочника Организаций, Зданий и Деятельности. "
        "Все запросы к /api/v1/* требуют заголовок X-API-Key."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router)


@app.get("/health", tags=["Health"])
def health_check():
    """Проверка доступности сервиса."""
    return {"status": "ok"}
