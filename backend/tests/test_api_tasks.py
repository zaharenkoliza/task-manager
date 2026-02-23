"""Tests for tasks API endpoints."""
from datetime import datetime, timezone

import pytest


class TestListTasks:
    """Tests for GET /api/tasks."""

    async def test_list_empty(self, client_with_data):
        """Returns empty list when no tasks."""
        response = await client_with_data.get("/api/tasks")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_with_tasks(self, client_with_tasks):
        """Returns all non-deleted tasks."""
        response = await client_with_tasks.get("/api/tasks")
        assert response.status_code == 200
        data = response.json()
        # Should not include deleted task (id=3)
        assert len(data) == 2
        ids = [t["id"] for t in data]
        assert 1 in ids
        assert 2 in ids
        assert 3 not in ids

    async def test_list_excludes_deleted(self, client_with_tasks):
        """Deleted tasks are not returned."""
        response = await client_with_tasks.get("/api/tasks")
        data = response.json()
        titles = [t["title"] for t in data]
        assert "Deleted Task" not in titles

    async def test_filter_by_status_id(self, client_with_tasks):
        """Can filter by status_id."""
        response = await client_with_tasks.get("/api/tasks?status_id=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status_id"] == 1

    async def test_filter_by_priority_id(self, client_with_tasks):
        """Can filter by priority_id."""
        response = await client_with_tasks.get("/api/tasks?priority_id=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["priority_id"] == 2

    async def test_filter_by_status_and_priority(self, client_with_tasks):
        """Can filter by both status and priority."""
        response = await client_with_tasks.get("/api/tasks?status_id=1&priority_id=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status_id"] == 1
        assert data[0]["priority_id"] == 1

    async def test_filter_no_match(self, client_with_tasks):
        """Filter with no matches returns empty list."""
        response = await client_with_tasks.get("/api/tasks?status_id=999")
        assert response.status_code == 200
        assert response.json() == []


class TestGetTask:
    """Tests for GET /api/tasks/{task_id}."""

    async def test_get_existing(self, client_with_tasks):
        """Returns task by id."""
        response = await client_with_tasks.get("/api/tasks/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Task 1"
        assert data["description"] == "Description 1"
        assert data["status_id"] == 1
        assert data["priority_id"] == 1

    async def test_get_task_without_description(self, client_with_tasks):
        """Returns task with null description."""
        response = await client_with_tasks.get("/api/tasks/2")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 2
        assert data["description"] is None

    async def test_get_deleted_returns_404(self, client_with_tasks):
        """Deleted task returns 404."""
        response = await client_with_tasks.get("/api/tasks/3")
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

    async def test_get_nonexistent(self, client_with_tasks):
        """Nonexistent task returns 404."""
        response = await client_with_tasks.get("/api/tasks/999")
        assert response.status_code == 404

    async def test_get_invalid_id(self, client_with_tasks):
        """Invalid id returns 422."""
        response = await client_with_tasks.get("/api/tasks/invalid")
        assert response.status_code == 422


class TestCreateTask:
    """Tests for POST /api/tasks."""

    async def test_create_minimal(self, client_with_data):
        """Creates task with only title."""
        response = await client_with_data.post(
            "/api/tasks",
            json={"title": "New Task"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] is None
        assert data["status_id"] == 1  # Default status
        assert data["priority_id"] == 2  # Default priority (Normal)
        assert data["id"] is not None
        assert data["deleted_at"] is None

    async def test_create_with_description(self, client_with_data):
        """Creates task with description."""
        response = await client_with_data.post(
            "/api/tasks",
            json={"title": "Task with Desc", "description": "My description"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Task with Desc"
        assert data["description"] == "My description"

    async def test_create_has_null_timestamps(self, client_with_data):
        """Created task has null start_time and end_time by default."""
        response = await client_with_data.post(
            "/api/tasks",
            json={"title": "Timestamped"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["start_time"] is None
        assert data["end_time"] is None
        assert data["created_at"] is not None

    async def test_create_missing_title(self, client_with_data):
        """Missing title returns 422."""
        response = await client_with_data.post(
            "/api/tasks",
            json={"description": "No title"},
        )
        assert response.status_code == 422

    async def test_create_empty_body(self, client_with_data):
        """Empty body returns 422."""
        response = await client_with_data.post("/api/tasks", json={})
        assert response.status_code == 422

    async def test_create_no_statuses_available(self, client):
        """Returns 400 if no statuses in database."""
        response = await client.post(
            "/api/tasks",
            json={"title": "Will Fail"},
        )
        assert response.status_code == 400
        assert "No statuses available" in response.json()["detail"]


class TestUpdateTask:
    """Tests for PATCH /api/tasks/{task_id}."""

    async def test_update_title(self, client_with_tasks):
        """Updates task title."""
        response = await client_with_tasks.patch(
            "/api/tasks/1",
            json={"title": "Updated Title"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        # Other fields unchanged
        assert data["description"] == "Description 1"

    async def test_update_description(self, client_with_tasks):
        """Updates task description."""
        response = await client_with_tasks.patch(
            "/api/tasks/1",
            json={"description": "New Description"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "New Description"

    async def test_update_status_id(self, client_with_tasks):
        """Updates task status."""
        response = await client_with_tasks.patch(
            "/api/tasks/1",
            json={"status_id": 2},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status_id"] == 2

    async def test_update_priority_id(self, client_with_tasks):
        """Updates task priority."""
        response = await client_with_tasks.patch(
            "/api/tasks/1",
            json={"priority_id": 3},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["priority_id"] == 3

    async def test_update_multiple_fields(self, client_with_tasks):
        """Updates multiple fields at once."""
        response = await client_with_tasks.patch(
            "/api/tasks/1",
            json={
                "title": "Multi Update",
                "description": "Multi Desc",
                "status_id": 3,
                "priority_id": 1,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Multi Update"
        assert data["description"] == "Multi Desc"
        assert data["status_id"] == 3
        assert data["priority_id"] == 1

    async def test_update_times(self, client_with_tasks):
        """Updates start and end times."""
        new_time = "2025-06-15T10:00:00Z"
        response = await client_with_tasks.patch(
            "/api/tasks/1",
            json={"start_time": new_time, "end_time": new_time},
        )
        assert response.status_code == 200
        data = response.json()
        assert "2025-06-15" in data["start_time"]

    async def test_update_nonexistent(self, client_with_tasks):
        """Updating nonexistent task returns 404."""
        response = await client_with_tasks.patch(
            "/api/tasks/999",
            json={"title": "Won't Work"},
        )
        assert response.status_code == 404

    async def test_update_deleted_task(self, client_with_tasks):
        """Updating deleted task returns 404."""
        response = await client_with_tasks.patch(
            "/api/tasks/3",
            json={"title": "Won't Work"},
        )
        assert response.status_code == 404

    async def test_update_invalid_status_id(self, client_with_tasks):
        """Invalid status_id returns 400."""
        response = await client_with_tasks.patch(
            "/api/tasks/1",
            json={"status_id": 999},
        )
        assert response.status_code == 400
        assert "Invalid status_id" in response.json()["detail"]

    async def test_update_invalid_priority_id(self, client_with_tasks):
        """Invalid priority_id returns 400."""
        response = await client_with_tasks.patch(
            "/api/tasks/1",
            json={"priority_id": 999},
        )
        assert response.status_code == 400
        assert "Invalid priority_id" in response.json()["detail"]

    async def test_update_empty_body(self, client_with_tasks):
        """Empty update body returns task unchanged."""
        response = await client_with_tasks.patch("/api/tasks/1", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Task 1"


class TestDeleteTask:
    """Tests for DELETE /api/tasks/{task_id}."""

    async def test_delete_existing(self, client_with_tasks):
        """Deletes (soft) existing task."""
        response = await client_with_tasks.delete("/api/tasks/1")
        assert response.status_code == 204

        # Verify task is no longer accessible
        get_response = await client_with_tasks.get("/api/tasks/1")
        assert get_response.status_code == 404

    async def test_delete_nonexistent(self, client_with_tasks):
        """Deleting nonexistent task returns 404."""
        response = await client_with_tasks.delete("/api/tasks/999")
        assert response.status_code == 404

    async def test_delete_already_deleted(self, client_with_tasks):
        """Deleting already deleted task returns 404."""
        response = await client_with_tasks.delete("/api/tasks/3")
        assert response.status_code == 404

    async def test_delete_removes_from_list(self, client_with_tasks):
        """Deleted task no longer appears in list."""
        # Get initial count
        list_response = await client_with_tasks.get("/api/tasks")
        initial_count = len(list_response.json())

        # Delete task
        await client_with_tasks.delete("/api/tasks/1")

        # Verify count decreased
        list_response = await client_with_tasks.get("/api/tasks")
        assert len(list_response.json()) == initial_count - 1

