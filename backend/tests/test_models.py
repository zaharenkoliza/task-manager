"""Tests for app.models module."""
from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.models import Task as TaskModel
from app.models import TaskPriority as TaskPriorityModel
from app.models import TaskStatus as TaskStatusModel


class TestTaskStatusModel:
    """Tests for TaskStatus model."""

    async def test_create_status(self, db_session):
        """Can create a status."""
        status = TaskStatusModel(title="New Status")
        db_session.add(status)
        await db_session.commit()

        result = await db_session.execute(select(TaskStatusModel))
        statuses = result.scalars().all()
        assert len(statuses) == 1
        assert statuses[0].title == "New Status"
        assert statuses[0].id is not None

    async def test_status_title_unique(self, db_session):
        """Status title must be unique."""
        from sqlalchemy.exc import IntegrityError

        status1 = TaskStatusModel(title="Duplicate")
        db_session.add(status1)
        await db_session.commit()

        status2 = TaskStatusModel(title="Duplicate")
        db_session.add(status2)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_status_tablename(self):
        """Table name is correct."""
        assert TaskStatusModel.__tablename__ == "task_statuses"


class TestTaskPriorityModel:
    """Tests for TaskPriority model."""

    async def test_create_priority(self, db_session):
        """Can create a priority."""
        priority = TaskPriorityModel(title="Urgent")
        db_session.add(priority)
        await db_session.commit()

        result = await db_session.execute(select(TaskPriorityModel))
        priorities = result.scalars().all()
        assert len(priorities) == 1
        assert priorities[0].title == "Urgent"

    async def test_priority_title_unique(self, db_session):
        """Priority title must be unique."""
        from sqlalchemy.exc import IntegrityError

        priority1 = TaskPriorityModel(title="Same")
        db_session.add(priority1)
        await db_session.commit()

        priority2 = TaskPriorityModel(title="Same")
        db_session.add(priority2)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_priority_tablename(self):
        """Table name is correct."""
        assert TaskPriorityModel.__tablename__ == "task_priorities"


class TestTaskModel:
    """Tests for Task model."""

    async def test_create_task(self, db_session_with_data):
        """Can create a task with required fields (without times)."""
        task = TaskModel(
            title="Test Task",
            status_id=1,
            priority_id=1,
        )
        db_session_with_data.add(task)
        await db_session_with_data.commit()

        result = await db_session_with_data.execute(select(TaskModel))
        tasks = result.scalars().all()
        assert len(tasks) == 1
        assert tasks[0].title == "Test Task"
        assert tasks[0].description is None
        assert tasks[0].deleted_at is None
        assert tasks[0].start_time is None
        assert tasks[0].end_time is None

    async def test_create_task_with_description(self, db_session_with_data):
        """Can create a task with description."""
        now = datetime.now(timezone.utc)
        task = TaskModel(
            title="Task with desc",
            description="This is a description",
            status_id=1,
            priority_id=2,
            start_time=now,
            end_time=now,
        )
        db_session_with_data.add(task)
        await db_session_with_data.commit()

        result = await db_session_with_data.execute(select(TaskModel))
        tasks = result.scalars().all()
        assert tasks[0].description == "This is a description"

    async def test_task_relationships(self, db_session_with_data):
        """Task has relationships to status and priority."""
        now = datetime.now(timezone.utc)
        task = TaskModel(
            title="Related Task",
            status_id=1,
            priority_id=2,
            start_time=now,
            end_time=now,
        )
        db_session_with_data.add(task)
        await db_session_with_data.commit()

        # Refresh to load relationships
        await db_session_with_data.refresh(task, ["status", "priority"])
        assert task.status.title == "To Do"
        assert task.priority.title == "Normal"

    async def test_task_soft_delete(self, db_session_with_data):
        """Task can be soft deleted."""
        now = datetime.now(timezone.utc)
        task = TaskModel(
            title="To Delete",
            status_id=1,
            priority_id=1,
            start_time=now,
            end_time=now,
        )
        db_session_with_data.add(task)
        await db_session_with_data.commit()

        # Soft delete
        task.deleted_at = datetime.now(timezone.utc)
        await db_session_with_data.commit()

        result = await db_session_with_data.execute(select(TaskModel))
        tasks = result.scalars().all()
        assert tasks[0].deleted_at is not None

    async def test_task_tablename(self):
        """Table name is correct."""
        assert TaskModel.__tablename__ == "tasks"

    async def test_status_has_tasks_relationship(self, db_session_with_data):
        """Status has back-reference to tasks."""
        now = datetime.now(timezone.utc)
        task = TaskModel(
            title="Task for status",
            status_id=1,
            priority_id=1,
            start_time=now,
            end_time=now,
        )
        db_session_with_data.add(task)
        await db_session_with_data.commit()

        result = await db_session_with_data.execute(
            select(TaskStatusModel).where(TaskStatusModel.id == 1)
        )
        status = result.scalar_one()
        await db_session_with_data.refresh(status, ["tasks"])
        assert len(status.tasks) == 1
        assert status.tasks[0].title == "Task for status"

    async def test_priority_has_tasks_relationship(self, db_session_with_data):
        """Priority has back-reference to tasks."""
        now = datetime.now(timezone.utc)
        task = TaskModel(
            title="Task for priority",
            status_id=1,
            priority_id=2,
            start_time=now,
            end_time=now,
        )
        db_session_with_data.add(task)
        await db_session_with_data.commit()

        result = await db_session_with_data.execute(
            select(TaskPriorityModel).where(TaskPriorityModel.id == 2)
        )
        priority = result.scalar_one()
        await db_session_with_data.refresh(priority, ["tasks"])
        assert len(priority.tasks) == 1
        assert priority.tasks[0].title == "Task for priority"
