"""Tests for app.schemas module."""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas import (
    TaskBase,
    TaskCreate,
    TaskPriority,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
)


class TestTaskStatus:
    """Tests for TaskStatus schema."""

    def test_valid_schema(self):
        """Valid data creates schema."""
        schema = TaskStatus(id=1, title="To Do")
        assert schema.id == 1
        assert schema.title == "To Do"

    def test_from_attributes(self):
        """Schema can be created from ORM-like object."""

        class FakeStatus:
            id = 1
            title = "In Progress"

        schema = TaskStatus.model_validate(FakeStatus())
        assert schema.id == 1
        assert schema.title == "In Progress"

    def test_missing_id_raises(self):
        """Missing id raises ValidationError."""
        with pytest.raises(ValidationError):
            TaskStatus(title="Test")

    def test_missing_title_raises(self):
        """Missing title raises ValidationError."""
        with pytest.raises(ValidationError):
            TaskStatus(id=1)


class TestTaskPriority:
    """Tests for TaskPriority schema."""

    def test_valid_schema(self):
        """Valid data creates schema."""
        schema = TaskPriority(id=1, title="High")
        assert schema.id == 1
        assert schema.title == "High"

    def test_from_attributes(self):
        """Schema can be created from ORM-like object."""

        class FakePriority:
            id = 2
            title = "Normal"

        schema = TaskPriority.model_validate(FakePriority())
        assert schema.id == 2
        assert schema.title == "Normal"


class TestTaskBase:
    """Tests for TaskBase schema."""

    def test_valid_with_description(self):
        """Valid data with description."""
        schema = TaskBase(title="My Task", description="Details")
        assert schema.title == "My Task"
        assert schema.description == "Details"

    def test_valid_without_description(self):
        """Valid data without description defaults to None."""
        schema = TaskBase(title="My Task")
        assert schema.title == "My Task"
        assert schema.description is None

    def test_missing_title_raises(self):
        """Missing title raises ValidationError."""
        with pytest.raises(ValidationError):
            TaskBase(description="No title")


class TestTaskCreate:
    """Tests for TaskCreate schema."""

    def test_inherits_from_base(self):
        """TaskCreate inherits from TaskBase."""
        schema = TaskCreate(title="New Task")
        assert schema.title == "New Task"
        assert schema.description is None

    def test_with_description(self):
        """TaskCreate with description."""
        schema = TaskCreate(title="New Task", description="Desc")
        assert schema.description == "Desc"


class TestTaskUpdate:
    """Tests for TaskUpdate schema."""

    def test_all_fields_optional(self):
        """All fields are optional."""
        schema = TaskUpdate()
        assert schema.title is None
        assert schema.description is None
        assert schema.start_time is None
        assert schema.end_time is None
        assert schema.status_id is None
        assert schema.priority_id is None

    def test_partial_update(self):
        """Partial fields can be set."""
        schema = TaskUpdate(title="Updated", status_id=2)
        assert schema.title == "Updated"
        assert schema.status_id == 2
        assert schema.description is None

    def test_datetime_fields(self):
        """Datetime fields are parsed correctly."""
        now = datetime.now(timezone.utc)
        schema = TaskUpdate(start_time=now, end_time=now)
        assert schema.start_time == now
        assert schema.end_time == now

    def test_model_dump_exclude_unset(self):
        """model_dump with exclude_unset returns only set fields."""
        schema = TaskUpdate(title="Only title")
        data = schema.model_dump(exclude_unset=True)
        assert data == {"title": "Only title"}


class TestTaskResponse:
    """Tests for TaskResponse schema."""

    def test_valid_schema(self):
        """Valid data creates schema."""
        now = datetime.now(timezone.utc)
        schema = TaskResponse(
            id=1,
            title="Task",
            description="Desc",
            status_id=1,
            priority_id=2,
            start_time=now,
            end_time=now,
            created_at=now,
            deleted_at=None,
        )
        assert schema.id == 1
        assert schema.title == "Task"
        assert schema.deleted_at is None

    def test_with_deleted_at(self):
        """Schema with deleted_at set."""
        now = datetime.now(timezone.utc)
        schema = TaskResponse(
            id=1,
            title="Deleted Task",
            description=None,
            status_id=1,
            priority_id=1,
            start_time=now,
            end_time=now,
            created_at=now,
            deleted_at=now,
        )
        assert schema.deleted_at == now

    def test_from_attributes(self):
        """Schema can be created from ORM-like object."""
        now = datetime.now(timezone.utc)

        class FakeTask:
            id = 5
            title = "Fake"
            description = "Fake desc"
            status_id = 2
            priority_id = 3
            start_time = now
            end_time = now
            created_at = now
            deleted_at = None

        schema = TaskResponse.model_validate(FakeTask())
        assert schema.id == 5
        assert schema.title == "Fake"

    def test_missing_required_field_raises(self):
        """Missing required field raises ValidationError."""
        with pytest.raises(ValidationError):
            TaskResponse(
                id=1,
                # missing title
                description=None,
                status_id=1,
                priority_id=1,
                start_time=datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                deleted_at=None,
            )
