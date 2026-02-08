"""Tests for API key authentication."""


class TestAuthentication:
    def test_no_api_key_returns_401(self, client):
        response = client.get("/api/v1/buildings/")
        assert response.status_code == 401
        assert "missing" in response.json()["detail"].lower()

    def test_wrong_api_key_returns_403(self, client):
        response = client.get(
            "/api/v1/buildings/",
            headers={"X-API-Key": "wrong-key"},
        )
        assert response.status_code == 403
        assert "invalid" in response.json()["detail"].lower()

    def test_correct_api_key_succeeds(self, client, api_headers):
        response = client.get("/api/v1/buildings/", headers=api_headers)
        assert response.status_code == 200
