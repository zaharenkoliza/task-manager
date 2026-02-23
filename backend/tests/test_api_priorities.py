"""Tests for priorities API endpoints."""
import pytest


class TestListPriorities:
    """Tests for GET /api/tasks/priorities."""

    async def test_list_empty(self, client):
        """Returns empty list when no priorities."""
        response = await client.get("/api/tasks/priorities")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_with_data(self, client_with_data):
        """Returns all priorities."""
        response = await client_with_data.get("/api/tasks/priorities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["id"] == 1
        assert data[0]["title"] == "High"
        assert data[1]["id"] == 2
        assert data[1]["title"] == "Normal"
        assert data[2]["id"] == 3
        assert data[2]["title"] == "Low"

    async def test_list_ordered_by_id(self, client_with_data):
        """Priorities are ordered by id."""
        response = await client_with_data.get("/api/tasks/priorities")
        data = response.json()
        ids = [p["id"] for p in data]
        assert ids == sorted(ids)


class TestGetPriority:
    """Tests for GET /api/tasks/priorities/{priority_id}."""

    async def test_get_existing(self, client_with_data):
        """Returns priority by id."""
        response = await client_with_data.get("/api/tasks/priorities/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "High"

    async def test_get_second_priority(self, client_with_data):
        """Returns second priority by id."""
        response = await client_with_data.get("/api/tasks/priorities/2")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 2
        assert data["title"] == "Normal"

    async def test_get_nonexistent(self, client_with_data):
        """Returns 404 for nonexistent priority."""
        response = await client_with_data.get("/api/tasks/priorities/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Priority not found"

    async def test_get_invalid_id(self, client_with_data):
        """Returns 422 for invalid id type."""
        response = await client_with_data.get("/api/tasks/priorities/invalid")
        assert response.status_code == 422

