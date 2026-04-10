"""Tests for BaseRepository and TaskRepository."""
from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task as TaskModel
from app.models import TaskPriority as TaskPriorityModel
from app.models import TaskStatus as TaskStatusModel
from app.repositories.base import BaseRepository
from app.repositories.task import TaskRepository


class TestBaseRepositoryGetSingle:
    """Tests for BaseRepository.get_single."""

    async def test_get_existing(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        result = await repo.get_single(1)
        assert result is not None
        assert result.id == 1
        assert result.title == "To Do"

    async def test_get_nonexistent(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        result = await repo.get_single(999)
        assert result is None


class TestBaseRepositoryGetMulti:
    """Tests for BaseRepository.get_multi."""

    async def test_get_multi_all(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        results = await repo.get_multi()
        assert len(results) == 3

    async def test_get_multi_with_filter(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        results = await repo.get_multi(id=1)
        assert len(results) == 1
        assert results[0].id == 1

    async def test_get_multi_with_offset(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        results = await repo.get_multi(offset=1)
        assert len(results) == 2

    async def test_get_multi_with_limit(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        results = await repo.get_multi(limit=1)
        assert len(results) == 1

    async def test_get_multi_with_order_by(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        results = await repo.get_multi(order_by=TaskStatusModel.title)
        assert len(results) == 3
        titles = [r.title for r in results]
        assert titles == sorted(titles)

    async def test_get_multi_no_match(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        results = await repo.get_multi(id=999)
        assert len(results) == 0


class TestBaseRepositoryGetAll:
    """Tests for BaseRepository.get_all."""

    async def test_get_all(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        results = await repo.get_all()
        assert len(results) == 3

    async def test_get_all_with_order_by(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        results = await repo.get_all(order_by=TaskStatusModel.title)
        titles = [r.title for r in results]
        assert titles == sorted(titles)

    async def test_get_all_empty(self, db_session: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session)
        results = await repo.get_all()
        assert len(results) == 0


class TestBaseRepositoryCreate:
    """Tests for BaseRepository.create."""

    async def test_create(self, db_session: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session)
        result = await repo.create(title="New Status")
        assert result.id is not None
        assert result.title == "New Status"

    async def test_create_with_id(self, db_session: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session)
        result = await repo.create(id=42, title="Custom ID")
        assert result.id == 42


class TestBaseRepositoryUpdate:
    """Tests for BaseRepository.update."""

    async def test_update_existing(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        result = await repo.update(1, title="Updated")
        assert result is not None
        assert result.title == "Updated"

    async def test_update_nonexistent(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        result = await repo.update(999, title="Won't Work")
        assert result is None


class TestBaseRepositoryDelete:
    """Tests for BaseRepository.delete."""

    async def test_delete_existing(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        result = await repo.delete(1)
        assert result is True
        assert await repo.get_single(1) is None

    async def test_delete_nonexistent(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        result = await repo.delete(999)
        assert result is False


class TestBaseRepositoryExists:
    """Tests for BaseRepository.exists."""

    async def test_exists_true(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        assert await repo.exists(1) is True

    async def test_exists_false(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        assert await repo.exists(999) is False


class TestBaseRepositoryGetExistingIds:
    """Tests for BaseRepository.get_existing_ids."""

    async def test_get_existing_ids(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        ids = await repo.get_existing_ids()
        assert ids == {1, 2, 3}

    async def test_get_existing_ids_empty(self, db_session: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session)
        ids = await repo.get_existing_ids()
        assert ids == set()


class TestBaseRepositoryCreateIfNotExists:
    """Tests for BaseRepository.create_if_not_exists."""

    async def test_create_if_not_exists_new(self, db_session: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session)
        result = await repo.create_if_not_exists(1, title="New")
        assert result is not None
        assert result.id == 1

    async def test_create_if_not_exists_existing(self, db_session_with_data: AsyncSession):
        repo = BaseRepository(TaskStatusModel, db_session_with_data)
        result = await repo.create_if_not_exists(1, title="Duplicate")
        assert result is None


class TestTaskRepositoryFilters:
    """Tests for TaskRepository time filters."""

    async def test_filter_by_start_time(self, db_session_with_tasks: AsyncSession):
        repo = TaskRepository(db_session_with_tasks)
        now = datetime.now(timezone.utc)
        results = await repo.get_multi(start_time=now)
        assert isinstance(results, list)

    async def test_filter_by_end_time(self, db_session_with_tasks: AsyncSession):
        repo = TaskRepository(db_session_with_tasks)
        now = datetime.now(timezone.utc)
        results = await repo.get_multi(end_time=now)
        assert isinstance(results, list)

    async def test_filter_by_start_and_end_time(self, db_session_with_tasks: AsyncSession):
        repo = TaskRepository(db_session_with_tasks)
        past = datetime(2000, 1, 1, tzinfo=timezone.utc)
        future = datetime(2100, 1, 1, tzinfo=timezone.utc)
        results = await repo.get_multi(start_time=past, end_time=future)
        assert len(results) == 2

    async def test_get_multi_with_order_by(self, db_session_with_tasks: AsyncSession):
        repo = TaskRepository(db_session_with_tasks)
        results = await repo.get_multi(order_by=TaskModel.title)
        assert len(results) == 2

    async def test_soft_delete(self, db_session_with_tasks: AsyncSession):
        repo = TaskRepository(db_session_with_tasks)
        result = await repo.soft_delete(1)
        assert result is True
        assert await repo.get_single(1) is None

    async def test_soft_delete_nonexistent(self, db_session_with_tasks: AsyncSession):
        repo = TaskRepository(db_session_with_tasks)
        result = await repo.soft_delete(999)
        assert result is False
