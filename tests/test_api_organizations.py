"""Tests for the organizations API endpoints."""


class TestGetOrganizationById:
    """Detail endpoint — no pagination, returns full OrganizationRead."""

    def test_success(self, client, api_headers, seed):
        org = seed["orgs"][0]
        response = client.get(f"/api/v1/organizations/{org.id}", headers=api_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == org.id
        assert data["name"] == org.name

    def test_not_found(self, client, api_headers):
        response = client.get("/api/v1/organizations/999", headers=api_headers)
        assert response.status_code == 404

    def test_response_has_nested_building(self, client, api_headers, seed):
        org = seed["orgs"][0]
        response = client.get(f"/api/v1/organizations/{org.id}", headers=api_headers)
        data = response.json()
        assert "building" in data
        assert data["building"]["id"] == org.building_id
        assert "address" in data["building"]

    def test_response_has_phones_list(self, client, api_headers, seed):
        org = seed["orgs"][0]
        response = client.get(f"/api/v1/organizations/{org.id}", headers=api_headers)
        data = response.json()
        assert "phones" in data
        assert isinstance(data["phones"], list)
        assert len(data["phones"]) > 0
        assert "phone_number" in data["phones"][0]

    def test_response_has_activities_list(self, client, api_headers, seed):
        org = seed["orgs"][0]
        response = client.get(f"/api/v1/organizations/{org.id}", headers=api_headers)
        data = response.json()
        assert "activities" in data
        assert isinstance(data["activities"], list)
        assert len(data["activities"]) > 0

    def test_org_without_phones_returns_empty_list(self, client, api_headers, seed):
        org_without_phones = next(
            o for o in seed["orgs"]
            if o.id not in {p.organization_id for p in seed["phones"]}
        )
        response = client.get(
            f"/api/v1/organizations/{org_without_phones.id}", headers=api_headers
        )
        data = response.json()
        assert data["phones"] == []

    def test_created_at_not_exposed(self, client, api_headers, seed):
        org = seed["orgs"][0]
        response = client.get(f"/api/v1/organizations/{org.id}", headers=api_headers)
        data = response.json()
        assert "created_at" not in data
        assert "created_at" not in data["building"]
        for phone in data["phones"]:
            assert "created_at" not in phone
        for activity in data["activities"]:
            assert "created_at" not in activity


class TestGetOrganizationsByBuilding:
    def test_returns_correct_count(self, client, api_headers, seed):
        building_id, expected_count = next(iter(seed["orgs_in_building"].items()))
        response = client.get(
            f"/api/v1/organizations/by-building/{building_id}", headers=api_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == expected_count
        assert len(data["results"]) == expected_count

    def test_all_returned_orgs_belong_to_building(self, client, api_headers, seed):
        building_id = seed["buildings"][0].id
        response = client.get(
            f"/api/v1/organizations/by-building/{building_id}", headers=api_headers
        )
        for org in response.json()["results"]:
            assert org["building_id"] == building_id

    def test_list_response_has_correct_fields(self, client, api_headers, seed):
        building_id = seed["buildings"][0].id
        response = client.get(
            f"/api/v1/organizations/by-building/{building_id}", headers=api_headers
        )
        expected_fields = {"id", "name", "building_id"}
        for org in response.json()["results"]:
            assert set(org.keys()) == expected_fields

    def test_nonexistent_building_returns_empty(self, client, api_headers):
        response = client.get(
            "/api/v1/organizations/by-building/999", headers=api_headers
        )
        assert response.status_code == 200
        assert response.json()["results"] == []
        assert response.json()["count"] == 0


class TestGetOrganizationsByActivity:
    def test_returns_organizations_with_activity(self, client, api_headers, seed):
        dairy_id = seed["activities"]["dairy"].id
        response = client.get(
            f"/api/v1/organizations/by-activity/{dairy_id}", headers=api_headers
        )
        assert response.status_code == 200
        expected = len(seed["direct_org_ids"].get(dairy_id, set()))
        assert response.json()["count"] == expected

    def test_unlinked_activity_returns_empty(self, client, api_headers, seed):
        trucks_id = seed["activities"]["trucks"].id
        response = client.get(
            f"/api/v1/organizations/by-activity/{trucks_id}", headers=api_headers
        )
        assert response.status_code == 200
        assert response.json()["results"] == []


class TestSearchByActivityRecursive:
    def test_root_returns_all_descendants_orgs(self, client, api_headers, seed):
        food_id = seed["activities"]["food"].id
        response = client.get(
            f"/api/v1/organizations/search/activity/{food_id}", headers=api_headers
        )
        assert response.status_code == 200
        expected = len(seed["recursive_org_ids"][food_id])
        assert response.json()["count"] == expected

    def test_leaf_returns_only_direct_orgs(self, client, api_headers, seed):
        parts_id = seed["activities"]["parts"].id
        response = client.get(
            f"/api/v1/organizations/search/activity/{parts_id}", headers=api_headers
        )
        assert response.status_code == 200
        expected = len(seed["recursive_org_ids"][parts_id])
        assert response.json()["count"] == expected

    def test_mid_level_includes_subtree(self, client, api_headers, seed):
        cars_id = seed["activities"]["cars"].id
        response = client.get(
            f"/api/v1/organizations/search/activity/{cars_id}", headers=api_headers
        )
        assert response.status_code == 200
        expected = len(seed["recursive_org_ids"][cars_id])
        assert response.json()["count"] == expected

    def test_nonexistent_activity_returns_empty(self, client, api_headers):
        response = client.get(
            "/api/v1/organizations/search/activity/9999", headers=api_headers
        )
        assert response.status_code == 200
        assert response.json()["count"] == 0
        assert response.json()["results"] == []


class TestSearchByName:
    def test_partial_match(self, client, api_headers, seed):
        org = seed["orgs"][1]
        partial = org.name[5:10]
        response = client.get(
            "/api/v1/organizations/search/name",
            params={"q": partial},
            headers=api_headers,
        )
        assert response.status_code == 200
        names = [o["name"] for o in response.json()["results"]]
        assert org.name in names

    def test_common_substring_returns_all(self, client, api_headers, seed):
        response = client.get(
            "/api/v1/organizations/search/name",
            params={"q": seed["org_common_substring"]},
            headers=api_headers,
        )
        assert response.status_code == 200
        assert response.json()["count"] == seed["org_count"]

    def test_no_results(self, client, api_headers):
        response = client.get(
            "/api/v1/organizations/search/name",
            params={"q": "xyzНесуществующая"},
            headers=api_headers,
        )
        assert response.status_code == 200
        assert response.json()["results"] == []
        assert response.json()["count"] == 0

    def test_empty_query_returns_422(self, client, api_headers):
        response = client.get(
            "/api/v1/organizations/search/name",
            params={"q": ""},
            headers=api_headers,
        )
        assert response.status_code == 422


class TestSearchInRadius:
    def test_finds_nearby(self, client, api_headers, seed):
        b = seed["moscow_buildings"][0]
        response = client.get(
            "/api/v1/organizations/search/radius",
            params={"lat": b.latitude, "lng": b.longitude, "radius": 1000},
            headers=api_headers,
        )
        assert response.status_code == 200
        assert response.json()["count"] >= 2

    def test_tiny_radius_excludes_distant(self, client, api_headers, seed):
        b = seed["moscow_buildings"][0]
        response = client.get(
            "/api/v1/organizations/search/radius",
            params={"lat": b.latitude, "lng": b.longitude, "radius": 10},
            headers=api_headers,
        )
        assert response.status_code == 200
        assert response.json()["count"] <= seed["orgs_in_building"][b.id]

    def test_missing_params_returns_422(self, client, api_headers):
        response = client.get(
            "/api/v1/organizations/search/radius",
            params={"lat": 55.0},
            headers=api_headers,
        )
        assert response.status_code == 422

    def test_invalid_latitude_returns_422(self, client, api_headers):
        response = client.get(
            "/api/v1/organizations/search/radius",
            params={"lat": 91, "lng": 37, "radius": 1000},
            headers=api_headers,
        )
        assert response.status_code == 422

    def test_invalid_longitude_returns_422(self, client, api_headers):
        response = client.get(
            "/api/v1/organizations/search/radius",
            params={"lat": 55, "lng": 181, "radius": 1000},
            headers=api_headers,
        )
        assert response.status_code == 422

    def test_zero_radius_returns_422(self, client, api_headers):
        response = client.get(
            "/api/v1/organizations/search/radius",
            params={"lat": 55, "lng": 37, "radius": 0},
            headers=api_headers,
        )
        assert response.status_code == 422

    def test_negative_radius_returns_422(self, client, api_headers):
        response = client.get(
            "/api/v1/organizations/search/radius",
            params={"lat": 55, "lng": 37, "radius": -100},
            headers=api_headers,
        )
        assert response.status_code == 422


class TestSearchInRectangle:
    def test_covers_region(self, client, api_headers, seed):
        moscow = seed["moscow_buildings"]
        lats = [b.latitude for b in moscow]
        lngs = [b.longitude for b in moscow]
        response = client.get(
            "/api/v1/organizations/search/rectangle",
            params={
                "lat_min": min(lats) - 0.01,
                "lat_max": max(lats) + 0.01,
                "lng_min": min(lngs) - 0.01,
                "lng_max": max(lngs) + 0.01,
            },
            headers=api_headers,
        )
        assert response.status_code == 200
        moscow_org_count = sum(
            seed["orgs_in_building"][b.id] for b in moscow
        )
        assert response.json()["count"] == moscow_org_count

    def test_excludes_outside(self, client, api_headers):
        response = client.get(
            "/api/v1/organizations/search/rectangle",
            params={"lat_min": 0, "lat_max": 1, "lng_min": 0, "lng_max": 1},
            headers=api_headers,
        )
        assert response.status_code == 200
        assert response.json()["results"] == []

    def test_missing_params_returns_422(self, client, api_headers):
        response = client.get(
            "/api/v1/organizations/search/rectangle",
            params={"lat_min": 55.0},
            headers=api_headers,
        )
        assert response.status_code == 422

    def test_invalid_lat_max_returns_422(self, client, api_headers):
        response = client.get(
            "/api/v1/organizations/search/rectangle",
            params={"lat_min": 55, "lat_max": 5562.80, "lng_min": 37, "lng_max": 38},
            headers=api_headers,
        )
        assert response.status_code == 422

    def test_lat_min_gte_lat_max_returns_422(self, client, api_headers):
        response = client.get(
            "/api/v1/organizations/search/rectangle",
            params={"lat_min": 56, "lat_max": 55, "lng_min": 37, "lng_max": 38},
            headers=api_headers,
        )
        assert response.status_code == 422

    def test_lng_min_gte_lng_max_returns_422(self, client, api_headers):
        response = client.get(
            "/api/v1/organizations/search/rectangle",
            params={"lat_min": 55, "lat_max": 56, "lng_min": 38, "lng_max": 37},
            headers=api_headers,
        )
        assert response.status_code == 422


class TestPagination:
    def test_limit_works(self, client, api_headers, seed):
        q = seed["org_common_substring"]
        response = client.get(
            "/api/v1/organizations/search/name",
            params={"q": q, "limit": 2},
            headers=api_headers,
        )
        data = response.json()
        assert len(data["results"]) == 2
        assert data["count"] == seed["org_count"]

    def test_offset_works(self, client, api_headers, seed):
        q = seed["org_common_substring"]
        response = client.get(
            "/api/v1/organizations/search/name",
            params={"q": q, "limit": 100, "offset": 2},
            headers=api_headers,
        )
        data = response.json()
        assert len(data["results"]) == seed["org_count"] - 2

    def test_limit_exceeds_max_returns_422(self, client, api_headers, seed):
        q = seed["org_common_substring"]
        response = client.get(
            "/api/v1/organizations/search/name",
            params={"q": q, "limit": 999},
            headers=api_headers,
        )
        assert response.status_code == 422

    def test_negative_offset_returns_422(self, client, api_headers, seed):
        q = seed["org_common_substring"]
        response = client.get(
            "/api/v1/organizations/search/name",
            params={"q": q, "offset": -1},
            headers=api_headers,
        )
        assert response.status_code == 422

    def test_next_and_previous_links(self, client, api_headers, seed):
        q = seed["org_common_substring"]
        response = client.get(
            "/api/v1/organizations/search/name",
            params={"q": q, "limit": 2, "offset": 0},
            headers=api_headers,
        )
        data = response.json()
        if seed["org_count"] > 2:
            assert data["next"] is not None
            assert "offset=2" in data["next"]
        assert data["previous"] is None

    def test_previous_link_present_when_offset(self, client, api_headers, seed):
        q = seed["org_common_substring"]
        response = client.get(
            "/api/v1/organizations/search/name",
            params={"q": q, "limit": 2, "offset": 2},
            headers=api_headers,
        )
        data = response.json()
        assert data["previous"] is not None
        assert "offset=0" in data["previous"]

    def test_default_pagination(self, client, api_headers, seed):
        q = seed["org_common_substring"]
        response = client.get(
            "/api/v1/organizations/search/name",
            params={"q": q},
            headers=api_headers,
        )
        data = response.json()
        assert data["count"] == seed["org_count"]
        # Default page_size (20) > org_count → всё на одной странице
        if seed["org_count"] <= 20:
            assert data["next"] is None
        assert data["previous"] is None
