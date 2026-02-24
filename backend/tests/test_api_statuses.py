"""Tests for statuses API endpoints."""
import pytest


class TestListStatuses:
    """Tests for GET /api/tasks/statuses."""

    async def test_list_empty(self, client):
        """Returns empty list when no statuses."""
        response = await client.get("/api/tasks/statuses")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_with_data(self, client_with_data):
        """Returns all statuses."""
        response = await client_with_data.get("/api/tasks/statuses")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["id"] == 1
        assert data[0]["title"] == "To Do"
        assert data[1]["id"] == 2
        assert data[1]["title"] == "In Progress"
        assert data[2]["id"] == 3
        assert data[2]["title"] == "Done"

    async def test_list_ordered_by_id(self, client_with_data):
        """Statuses are ordered by id."""
        response = await client_with_data.get("/api/tasks/statuses")
        data = response.json()
        ids = [s["id"] for s in data]
        assert ids == sorted(ids)


class TestGetStatus:
    """Tests for GET /api/tasks/statuses/{status_id}."""

    async def test_get_existing(self, client_with_data):
        """Returns status by id."""
        response = await client_with_data.get("/api/tasks/statuses/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "To Do"

    async def test_get_second_status(self, client_with_data):
        """Returns second status by id."""
        response = await client_with_data.get("/api/tasks/statuses/2")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 2
        assert data["title"] == "In Progress"

    async def test_get_nonexistent(self, client_with_data):
        """Returns 404 for nonexistent status."""
        response = await client_with_data.get("/api/tasks/statuses/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Status not found"

    async def test_get_invalid_id(self, client_with_data):
        """Returns 422 for invalid id type."""
        response = await client_with_data.get("/api/tasks/statuses/invalid")
        assert response.status_code == 422

