"""Unit tests for the repository layer."""

from app.repositories.activity import ActivityRepository
from app.repositories.building import BuildingRepository
from app.repositories.organization import OrganizationRepository

# Large limit to fetch all items in repo tests
ALL = dict(limit=100, offset=0)


class TestOrganizationRepository:
    def test_get_by_id_returns_org(self, db_session, seed):
        repo = OrganizationRepository(db_session)
        org = seed["orgs"][0]
        result = repo.get_by_id(org.id)
        assert result is not None
        assert result.id == org.id
        assert result.name == org.name

    def test_get_by_id_returns_none(self, db_session):
        repo = OrganizationRepository(db_session)
        assert repo.get_by_id(999) is None

    def test_get_by_building_id(self, db_session, seed):
        repo = OrganizationRepository(db_session)
        building_id = seed["buildings"][0].id
        items, total = repo.get_by_building_id(building_id, **ALL)
        assert total == seed["orgs_in_building"][building_id]
        assert all(o.building_id == building_id for o in items)

    def test_get_by_activity_id(self, db_session, seed):
        repo = OrganizationRepository(db_session)
        meat_id = seed["activities"]["meat"].id
        items, total = repo.get_by_activity_id(meat_id, **ALL)
        expected = len(seed["direct_org_ids"].get(meat_id, set()))
        assert total == expected

    def test_get_by_activity_ids(self, db_session, seed):
        repo = OrganizationRepository(db_session)
        meat_id = seed["activities"]["meat"].id
        dairy_id = seed["activities"]["dairy"].id
        items, total = repo.get_by_activity_ids([meat_id, dairy_id], **ALL)
        expected_orgs = (
            seed["direct_org_ids"].get(meat_id, set())
            | seed["direct_org_ids"].get(dairy_id, set())
        )
        assert total == len(expected_orgs)

    def test_search_by_name_finds_match(self, db_session, seed):
        repo = OrganizationRepository(db_session)
        org = seed["orgs"][2]
        partial = org.name[5:10]
        items, total = repo.search_by_name(partial, **ALL)
        assert any(o.id == org.id for o in items)

    def test_search_by_name_case_insensitive(self, db_session, seed):
        repo = OrganizationRepository(db_session)
        org = seed["orgs"][2]
        partial = org.name[5:10].lower()
        items, total = repo.search_by_name(partial, **ALL)
        assert total >= 1

    def test_search_in_radius(self, db_session, seed):
        repo = OrganizationRepository(db_session)
        b = seed["moscow_buildings"][0]
        items, total = repo.search_in_radius(b.latitude, b.longitude, 1000, **ALL)
        assert total >= 2

    def test_search_in_radius_excludes_far_away(self, db_session, seed):
        repo = OrganizationRepository(db_session)
        b = seed["moscow_buildings"][0]
        items, total = repo.search_in_radius(b.latitude, b.longitude, 10, **ALL)
        assert total <= seed["orgs_in_building"][b.id]

    def test_search_in_rectangle(self, db_session, seed):
        repo = OrganizationRepository(db_session)
        moscow = seed["moscow_buildings"]
        lats = [b.latitude for b in moscow]
        lngs = [b.longitude for b in moscow]
        items, total = repo.search_in_rectangle(
            min(lats) - 0.01, max(lats) + 0.01,
            min(lngs) - 0.01, max(lngs) + 0.01,
            **ALL,
        )
        assert total >= 2

    def test_search_in_rectangle_no_results(self, db_session):
        repo = OrganizationRepository(db_session)
        items, total = repo.search_in_rectangle(0.0, 0.1, 0.0, 0.1, **ALL)
        assert total == 0


class TestActivityRepository:
    def test_get_all(self, db_session, seed):
        repo = ActivityRepository(db_session)
        assert len(repo.get_all()) == seed["activity_count"]

    def test_get_by_id(self, db_session, seed):
        repo = ActivityRepository(db_session)
        food = seed["activities"]["food"]
        result = repo.get_by_id(food.id)
        assert result is not None
        assert result.name == food.name

    def test_get_by_id_none(self, db_session):
        repo = ActivityRepository(db_session)
        assert repo.get_by_id(999) is None

    def test_get_root_activities(self, db_session, seed):
        repo = ActivityRepository(db_session)
        roots = repo.get_root_activities()
        assert len(roots) == seed["root_activity_count"]
        assert all(r.parent_id is None for r in roots)

    def test_get_descendants_from_root(self, db_session, seed):
        repo = ActivityRepository(db_session)
        food = seed["activities"]["food"]
        ids = repo.get_descendant_ids(food.id)
        assert food.id in ids
        assert len(ids) == len(seed["activity_descendant_ids"][food.id])

    def test_get_descendants_from_mid(self, db_session, seed):
        repo = ActivityRepository(db_session)
        passenger = seed["activities"]["passenger"]
        ids = repo.get_descendant_ids(passenger.id)
        assert passenger.id in ids
        assert len(ids) == len(seed["activity_descendant_ids"][passenger.id])

    def test_get_descendants_leaf_returns_self(self, db_session, seed):
        repo = ActivityRepository(db_session)
        parts = seed["activities"]["parts"]
        ids = repo.get_descendant_ids(parts.id)
        assert ids == [parts.id]

    def test_get_descendants_include_self_false(self, db_session, seed):
        repo = ActivityRepository(db_session)
        food = seed["activities"]["food"]
        ids = repo.get_descendant_ids(food.id, include_self=False)
        assert food.id not in ids
        expected = seed["activity_descendant_ids"][food.id] - {food.id}
        assert len(ids) == len(expected)

    def test_get_descendants_leaf_include_self_false(self, db_session, seed):
        repo = ActivityRepository(db_session)
        parts = seed["activities"]["parts"]
        ids = repo.get_descendant_ids(parts.id, include_self=False)
        assert ids == []


class TestBuildingRepository:
    def test_get_all(self, db_session, seed):
        repo = BuildingRepository(db_session)
        items, total = repo.get_all(**ALL)
        assert total == seed["building_count"]
        assert len(items) == total

    def test_get_by_id(self, db_session, seed):
        repo = BuildingRepository(db_session)
        b = seed["buildings"][0]
        result = repo.get_by_id(b.id)
        assert result is not None
        assert result.address == b.address

    def test_get_by_id_none(self, db_session):
        repo = BuildingRepository(db_session)
        assert repo.get_by_id(999) is None
