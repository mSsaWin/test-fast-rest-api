"""
Test configuration and fixtures.

Environment variables are set BEFORE importing any app modules so that
pydantic-settings picks up test values instead of production defaults.
"""

import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/test_directory_db",
)
os.environ["API_KEY"] = "test-api-key"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.database import Base  # noqa: E402
from app.dependencies import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import *  # noqa: E402, F401, F403 — register all models
from app.models.activity import Activity  # noqa: E402
from app.models.building import Building  # noqa: E402
from app.models.organization import (  # noqa: E402
    Organization,
    OrganizationPhone,
    organization_activities,
)

TEST_DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


# ── Database lifecycle ─────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Drop and re-create all tables once per test session."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _seed_test_data(session) -> dict:  # noqa: ANN001
    """Insert minimal test data. Returns dict of created objects for reference."""

    # ── Buildings ───────────────────────────────────────────────
    buildings = [
        Building(id=1, address="г. Москва, ул. Ленина 1", latitude=55.7558, longitude=37.6173),
        Building(id=2, address="г. Москва, ул. Пушкина 5", latitude=55.7601, longitude=37.6186),
        Building(id=3, address="г. Новосибирск, ул. Блюхера 32/1", latitude=55.0084, longitude=82.9357),
    ]
    session.add_all(buildings)
    session.flush()

    # ── Activities (tree: 2 roots, max 3 levels) ───────────────
    activities = {
        "food":      Activity(id=1, name="Еда", parent_id=None, level=1),
        "meat":      Activity(id=2, name="Мясная продукция", parent_id=1, level=2),
        "dairy":     Activity(id=3, name="Молочная продукция", parent_id=1, level=2),
        "cars":      Activity(id=4, name="Автомобили", parent_id=None, level=1),
        "trucks":    Activity(id=5, name="Грузовые", parent_id=4, level=2),
        "passenger": Activity(id=6, name="Легковые", parent_id=4, level=2),
        "parts":     Activity(id=7, name="Запчасти", parent_id=6, level=3),
    }
    session.add_all(activities.values())
    session.flush()

    # ── Organizations ──────────────────────────────────────────
    orgs = [
        Organization(id=1, name='ООО "Рога и Копыта"', building_id=1),
        Organization(id=2, name='ООО "Молочный мир"', building_id=1),
        Organization(id=3, name='ООО "АвтоПлюс"', building_id=2),
        Organization(id=4, name='ООО "Мясной двор"', building_id=3),
    ]
    session.add_all(orgs)
    session.flush()

    # ── Phones ─────────────────────────────────────────────────
    phones = [
        OrganizationPhone(organization_id=1, phone_number="2-222-222"),
        OrganizationPhone(organization_id=1, phone_number="3-333-333"),
        OrganizationPhone(organization_id=2, phone_number="8-923-666-13-13"),
        OrganizationPhone(organization_id=3, phone_number="8-495-100-20-30"),
    ]
    session.add_all(phones)
    session.flush()

    # ── Organization ↔ Activity links ──────────────────────────
    # org1 → meat, dairy   | org2 → dairy
    # org3 → passenger, parts | org4 → meat
    links = [(1, 2), (1, 3), (2, 3), (3, 6), (3, 7), (4, 2)]
    for org_id, act_id in links:
        session.execute(
            organization_activities.insert().values(
                organization_id=org_id, activity_id=act_id
            )
        )
    session.flush()

    # ── Computed helpers (derived from data above) ─────────────
    orgs_in_building: dict[int, int] = {}
    for org in orgs:
        orgs_in_building[org.building_id] = orgs_in_building.get(org.building_id, 0) + 1

    # activity_id → set of org_ids linked directly
    direct_org_ids: dict[int, set[int]] = {}
    for org_id, act_id in links:
        direct_org_ids.setdefault(act_id, set()).add(org_id)

    # activity_id → set of child activity_ids
    activity_children: dict[int, set[int]] = {}
    for act in activities.values():
        if act.parent_id is not None:
            activity_children.setdefault(act.parent_id, set()).add(act.id)

    def _descendant_ids(act_id: int) -> set[int]:
        """All descendant activity IDs including self."""
        result = {act_id}
        for child_id in activity_children.get(act_id, set()):
            result |= _descendant_ids(child_id)
        return result

    # activity_id → total org count (recursive, including subtree)
    recursive_org_ids: dict[int, set[int]] = {}
    for act in activities.values():
        desc_act_ids = _descendant_ids(act.id)
        org_set: set[int] = set()
        for d_id in desc_act_ids:
            org_set |= direct_org_ids.get(d_id, set())
        recursive_org_ids[act.id] = org_set

    root_activities = [a for a in activities.values() if a.parent_id is None]

    # Общая подстрока, которая есть во ВСЕХ именах организаций
    org_common_substring = "ООО"
    assert all(org_common_substring in o.name for o in orgs), (
        f"Все организации должны содержать '{org_common_substring}' в имени"
    )

    return {
        "buildings": buildings,
        "activities": activities,
        "orgs": orgs,
        "phones": phones,
        "links": links,
        # Convenience counts
        "building_count": len(buildings),
        "activity_count": len(activities),
        "org_count": len(orgs),
        "orgs_in_building": orgs_in_building,
        "root_activity_count": len(root_activities),
        "moscow_buildings": [b for b in buildings if b.latitude > 55.5 and b.longitude < 40],
        # Activity → org mappings
        "direct_org_ids": direct_org_ids,
        "recursive_org_ids": recursive_org_ids,
        "org_common_substring": org_common_substring,
        # Activity → descendant activity IDs (including self)
        "activity_descendant_ids": {
            act.id: _descendant_ids(act.id) for act in activities.values()
        },
    }


# ── Per-test fixtures ──────────────────────────────────────────

@pytest.fixture()
def db_session(setup_database):
    """
    Provide a transactional database session that is rolled back
    after each test — ensures complete isolation between tests.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    session._seed = _seed_test_data(session)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def seed(db_session):
    """Access to seeded test data references."""
    return db_session._seed


@pytest.fixture()
def client(db_session):
    """FastAPI TestClient with the DB dependency overridden."""

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture()
def api_headers():
    """Valid API-key headers for authenticated requests."""
    return {"X-API-Key": "test-api-key"}
