"""Tests for health check endpoint."""
import pytest


class TestHealthCheck:
    """Tests for /health endpoint."""

    async def test_health_check(self, client):
        """Health check returns ok status."""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

