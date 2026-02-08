"""Tests for the buildings API endpoints."""

REQUIRED_FIELDS = {"id", "address", "latitude", "longitude"}


class TestGetBuildings:
    def test_returns_paginated_response(self, client, api_headers, seed):
        response = client.get("/api/v1/buildings/", headers=api_headers)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "count" in data
        assert "next" in data
        assert "previous" in data
        assert data["count"] == seed["building_count"]
        assert len(data["results"]) == seed["building_count"]

    def test_buildings_have_required_fields(self, client, api_headers, seed):
        response = client.get("/api/v1/buildings/", headers=api_headers)
        results = response.json()["results"]
        assert len(results) == seed["building_count"]
        for building in results:
            assert REQUIRED_FIELDS.issubset(building.keys())

    def test_coordinates_are_valid(self, client, api_headers, seed):
        response = client.get("/api/v1/buildings/", headers=api_headers)
        results = response.json()["results"]
        assert len(results) == seed["building_count"]
        for b in results:
            assert -90 <= b["latitude"] <= 90
            assert -180 <= b["longitude"] <= 180

    def test_addresses_are_non_empty_strings(self, client, api_headers, seed):
        response = client.get("/api/v1/buildings/", headers=api_headers)
        results = response.json()["results"]
        assert len(results) == seed["building_count"]
        for b in results:
            assert isinstance(b["address"], str)
            assert len(b["address"]) > 0

    def test_created_at_not_exposed(self, client, api_headers, seed):
        response = client.get("/api/v1/buildings/", headers=api_headers)
        results = response.json()["results"]
        assert len(results) > 0
        for b in results:
            assert "created_at" not in b

    def test_all_seeded_buildings_present(self, client, api_headers, seed):
        response = client.get("/api/v1/buildings/", headers=api_headers)
        returned_ids = {b["id"] for b in response.json()["results"]}
        seeded_ids = {b.id for b in seed["buildings"]}
        assert returned_ids == seeded_ids

    def test_limit_param(self, client, api_headers):
        response = client.get(
            "/api/v1/buildings/", params={"limit": 1}, headers=api_headers
        )
        data = response.json()
        assert len(data["results"]) == 1

    def test_offset_param(self, client, api_headers, seed):
        response = client.get(
            "/api/v1/buildings/",
            params={"limit": 100, "offset": 1},
            headers=api_headers,
        )
        data = response.json()
        assert len(data["results"]) == seed["building_count"] - 1

    def test_limit_exceeds_max_returns_422(self, client, api_headers):
        response = client.get(
            "/api/v1/buildings/", params={"limit": 999}, headers=api_headers
        )
        assert response.status_code == 422

    def test_next_link_present_when_more_pages(self, client, api_headers, seed):
        response = client.get(
            "/api/v1/buildings/", params={"limit": 1}, headers=api_headers
        )
        data = response.json()
        if seed["building_count"] > 1:
            assert data["next"] is not None
            assert "offset=1" in data["next"]
        assert data["previous"] is None

    def test_previous_link_present_when_offset(self, client, api_headers):
        response = client.get(
            "/api/v1/buildings/", params={"limit": 1, "offset": 1}, headers=api_headers
        )
        data = response.json()
        assert data["previous"] is not None
        assert "offset=0" in data["previous"]

    def test_no_next_on_last_page(self, client, api_headers, seed):
        response = client.get(
            "/api/v1/buildings/",
            params={"limit": 100, "offset": 0},
            headers=api_headers,
        )
        data = response.json()
        assert data["next"] is None
        assert data["previous"] is None
