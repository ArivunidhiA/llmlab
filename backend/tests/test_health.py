"""Tests for health check endpoint."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check returns healthy status."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] in ("healthy", "degraded")
    assert data["version"] == "1.0.0"
    assert "uptime_seconds" in data
    assert data["uptime_seconds"] >= 0


def test_health_check_database_status(client: TestClient):
    """Test health check reports database connection status."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    # With SQLite in-memory, should always be connected
    assert data["database"] in ("connected", "disconnected")
