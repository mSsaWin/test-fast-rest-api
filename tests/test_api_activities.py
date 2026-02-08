"""Tests for the activities API endpoints."""


class TestGetActivities:
    def test_returns_tree_structure(self, client, api_headers, seed):
        response = client.get("/api/v1/activities/", headers=api_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == seed["root_activity_count"]

    def test_root_nodes_have_children(self, client, api_headers, seed):
        response = client.get("/api/v1/activities/", headers=api_headers)
        data = response.json()
        assert len(data) == seed["root_activity_count"]
        for root in data:
            assert "children" in root
            assert isinstance(root["children"], list)
            assert len(root["children"]) > 0

    def test_tree_respects_level_hierarchy(self, client, api_headers, seed):
        """Level 1 → children level 2 → grandchildren level 3."""
        response = client.get("/api/v1/activities/", headers=api_headers)
        data = response.json()
        assert len(data) > 0
        for root in data:
            assert root["level"] == 1
            for child in root["children"]:
                assert child["level"] == 2
                for grandchild in child["children"]:
                    assert grandchild["level"] == 3

    def test_nodes_have_required_fields(self, client, api_headers, seed):
        response = client.get("/api/v1/activities/", headers=api_headers)
        data = response.json()
        assert len(data) == seed["root_activity_count"]
        required = {"id", "name", "level", "children"}
        for root in data:
            assert required.issubset(root.keys())

    def test_total_activity_count_matches_seed(self, client, api_headers, seed):
        """Flatten the tree and count — should match seed."""
        response = client.get("/api/v1/activities/", headers=api_headers)

        def count_nodes(nodes):
            total = 0
            for node in nodes:
                total += 1 + count_nodes(node.get("children", []))
            return total

        assert count_nodes(response.json()) == seed["activity_count"]
