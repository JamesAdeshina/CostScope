"""
Tests for CostScope API health endpoints.
"""

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """The health endpoint should report a healthy API."""

    response = client.get("/health")

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["service"] == "CostScope API"
    assert "timestamp" in payload
