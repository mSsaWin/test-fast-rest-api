# Organization Directory REST API

REST API справочник организаций, зданий и видов деятельности.

## Стек технологий

- **FastAPI** — веб-фреймворк
- **Pydantic v2** — валидация и сериализация
- **SQLAlchemy 2.0** — ORM
- **Alembic** — миграции БД
- **PostgreSQL 16** — база данных
- **Docker & Docker Compose** — контейнеризация
- **pytest** — тестирование (100 тестов)

## Архитектура

Слоистая архитектура с разделением ответственности:

```
Router (API) → Service (бизнес-логика) → Repository (доступ к данным) → Model (ORM)
```

```
app/
├── api/              # HTTP-эндпоинты (роутеры FastAPI)
├── services/         # Бизнес-логика
├── repositories/     # SQL-запросы и работа с БД
├── models/           # SQLAlchemy-модели (ORM)
├── schemas/          # Pydantic-схемы (валидация, сериализация)
├── utils/            # Утилиты (геовычисления, пагинация)
├── config.py         # Конфигурация (Pydantic Settings)
├── database.py       # Движок SQLAlchemy, фабрика сессий
├── dependencies.py   # FastAPI-зависимости (get_db, auth, pagination)
└── main.py           # Точка входа приложения
alembic/              # Миграции БД
tests/                # Тесты (API, service, repository)
```

## Быстрый старт

### Требования

- Docker и Docker Compose

### Запуск

```bash
git clone https://github.com/mSsaWin/test-fast-rest-api.git
cd test-fast-rest-api
docker compose up --build
```

При первом запуске автоматически:
- создаётся БД PostgreSQL
- применяются миграции Alembic
- заполняются тестовые данные (seed)
- запускается сервер

Приложение доступно:
- API: http://localhost:8000/api/v1/
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

### Запуск тестов

```bash
docker compose --profile test run --rm test
```

## Аутентификация

Все запросы к `/api/v1/*` требуют заголовок `X-API-Key`.

По умолчанию: `my-secret-api-key` (переопределяется через `API_KEY`).

## API Endpoints

Все списковые эндпоинты поддерживают пагинацию: `?limit=20&offset=0`.

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/v1/buildings/` | Список зданий |
| GET | `/api/v1/activities/` | Дерево видов деятельности |
| GET | `/api/v1/organizations/{id}` | Организация по ID (полная информация) |
| GET | `/api/v1/organizations/by-building/{id}` | Организации в здании |
| GET | `/api/v1/organizations/by-activity/{id}` | Организации по виду деятельности |
| GET | `/api/v1/organizations/search/activity/{id}` | Поиск с учётом вложенных деятельностей |
| GET | `/api/v1/organizations/search/name?q=...` | Поиск по названию (ILIKE) |
| GET | `/api/v1/organizations/search/radius` | Геопоиск в радиусе |
| GET | `/api/v1/organizations/search/rectangle` | Геопоиск в прямоугольнике |

### Геопоиск

**По радиусу** (Haversine + bounding box предфильтр):
```
GET /api/v1/organizations/search/radius?lat=55.758&lng=37.618&radius=1000
```
- `lat` [-90, 90], `lng` [-180, 180] — координаты центра
- `radius` — радиус в метрах (>0)

**По прямоугольнику:**
```
GET /api/v1/organizations/search/rectangle?lat_min=55.75&lat_max=55.77&lng_min=37.61&lng_max=37.63
```

### Пагинация

Ответ в DRF-стиле:
```json
{
  "count": 42,
  "next": "http://.../api/v1/buildings/?limit=20&offset=20",
  "previous": null,
  "results": [...]
}
```

Параметры: `limit` (1–100, по умолчанию 20), `offset` (>=0, по умолчанию 0).

## Примеры запросов

```bash
# Список зданий
curl -H "X-API-Key: my-secret-api-key" "http://localhost:8000/api/v1/buildings/?limit=5"

# Дерево деятельностей
curl -H "X-API-Key: my-secret-api-key" http://localhost:8000/api/v1/activities/

# Организация по ID
curl -H "X-API-Key: my-secret-api-key" http://localhost:8000/api/v1/organizations/1

# Организации в здании
curl -H "X-API-Key: my-secret-api-key" "http://localhost:8000/api/v1/organizations/by-building/1?limit=10"

# Поиск по названию
curl -H "X-API-Key: my-secret-api-key" "http://localhost:8000/api/v1/organizations/search/name?q=Молоч"

# Рекурсивный поиск по деятельности «Еда» (включая подкатегории)
curl -H "X-API-Key: my-secret-api-key" http://localhost:8000/api/v1/organizations/search/activity/1

# Поиск в радиусе 1 км
curl -H "X-API-Key: my-secret-api-key" "http://localhost:8000/api/v1/organizations/search/radius?lat=55.758&lng=37.618&radius=1000"

# Поиск в прямоугольнике
curl -H "X-API-Key: my-secret-api-key" "http://localhost:8000/api/v1/organizations/search/rectangle?lat_min=55.75&lat_max=55.77&lng_min=37.61&lng_max=37.63"
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | URL подключения к PostgreSQL | `postgresql://postgres:postgres@db:5432/directory_db` |
| `API_KEY` | Статический API-ключ | `my-secret-api-key` |
| `PAGE_SIZE_DEFAULT` | Размер страницы по умолчанию | `20` |
| `PAGE_SIZE_MAX` | Максимальный размер страницы | `100` |
