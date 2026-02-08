"""Unit tests for the service layer."""

import pytest
from fastapi import HTTPException

from app.services.activity import ActivityService
from app.services.building import BuildingService
from app.services.organization import OrganizationService

# Large limit to fetch all items in service/repo tests
ALL = dict(limit=100, offset=0)


class TestOrganizationService:
    def test_get_by_id_exists(self, db_session, seed):
        service = OrganizationService(db_session)
        org = seed["orgs"][0]
        result = service.get_by_id(org.id)
        assert result.id == org.id
        assert result.name == org.name

    def test_get_by_id_not_found_raises_404(self, db_session):
        service = OrganizationService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            service.get_by_id(999)
        assert exc_info.value.status_code == 404

    def test_get_by_building(self, db_session, seed):
        service = OrganizationService(db_session)
        building_id = seed["buildings"][0].id
        items, total = service.get_by_building(building_id, **ALL)
        assert total == seed["orgs_in_building"][building_id]
        assert len(items) == total

    def test_get_by_building_empty(self, db_session):
        service = OrganizationService(db_session)
        items, total = service.get_by_building(999, **ALL)
        assert items == []
        assert total == 0

    def test_get_by_activity(self, db_session, seed):
        service = OrganizationService(db_session)
        dairy_id = seed["activities"]["dairy"].id
        items, total = service.get_by_activity(dairy_id, **ALL)
        expected = len(seed["direct_org_ids"].get(dairy_id, set()))
        assert total == expected

    def test_search_by_activity_recursive(self, db_session, seed):
        service = OrganizationService(db_session)
        food_id = seed["activities"]["food"].id
        items, total = service.search_by_activity_recursive(food_id, **ALL)
        expected = len(seed["recursive_org_ids"][food_id])
        assert total == expected

    def test_search_by_name(self, db_session, seed):
        service = OrganizationService(db_session)
        org = seed["orgs"][1]
        partial = org.name[5:10]
        items, total = service.search_by_name(partial, **ALL)
        assert any(r.id == org.id for r in items)

    def test_search_in_radius(self, db_session, seed):
        service = OrganizationService(db_session)
        b = seed["moscow_buildings"][0]
        items, total = service.search_in_radius(b.latitude, b.longitude, 1000, **ALL)
        assert total >= 2

    def test_search_in_rectangle(self, db_session, seed):
        service = OrganizationService(db_session)
        moscow = seed["moscow_buildings"]
        lats = [b.latitude for b in moscow]
        lngs = [b.longitude for b in moscow]
        items, total = service.search_in_rectangle(
            min(lats) - 0.01, max(lats) + 0.01,
            min(lngs) - 0.01, max(lngs) + 0.01,
            **ALL,
        )
        assert total >= 2


class TestActivityService:
    def test_get_tree_root_count(self, db_session, seed):
        service = ActivityService(db_session)
        tree = service.get_tree()
        assert len(tree) == seed["root_activity_count"]

    def test_get_tree_has_children(self, db_session):
        service = ActivityService(db_session)
        tree = service.get_tree()
        for root in tree:
            assert hasattr(root, "children")
            assert len(root.children) > 0

    def test_get_descendant_ids_root(self, db_session, seed):
        service = ActivityService(db_session)
        food_id = seed["activities"]["food"].id
        ids = service.get_descendant_ids(food_id)
        assert food_id in ids
        assert len(ids) == len(seed["activity_descendant_ids"][food_id])

    def test_get_descendant_ids_mid(self, db_session, seed):
        service = ActivityService(db_session)
        cars_id = seed["activities"]["cars"].id
        ids = service.get_descendant_ids(cars_id)
        assert cars_id in ids
        assert len(ids) == len(seed["activity_descendant_ids"][cars_id])

    def test_get_descendant_ids_leaf(self, db_session, seed):
        service = ActivityService(db_session)
        parts_id = seed["activities"]["parts"].id
        ids = service.get_descendant_ids(parts_id)
        assert ids == [parts_id]

    def test_get_descendant_ids_exclude_self(self, db_session, seed):
        service = ActivityService(db_session)
        food_id = seed["activities"]["food"].id
        ids = service.get_descendant_ids(food_id, include_self=False)
        assert food_id not in ids
        expected = seed["activity_descendant_ids"][food_id] - {food_id}
        assert len(ids) == len(expected)


class TestBuildingService:
    def test_get_all(self, db_session, seed):
        service = BuildingService(db_session)
        items, total = service.get_all(**ALL)
        assert total == seed["building_count"]
        assert len(items) == total
