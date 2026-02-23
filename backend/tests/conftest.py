"""Pytest fixtures for testing."""
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import Base, get_session
from app.main import app
from app.models import Task as TaskModel
from app.models import TaskPriority as TaskPriorityModel
from app.models import TaskStatus as TaskStatusModel


# In-memory SQLite for tests (async via aiosqlite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def async_engine():
    """Create async engine for tests."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with async_session_maker() as session:
        yield session


@pytest.fixture
async def db_session_with_data(db_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with seed data."""
    # Add statuses
    statuses = [
        TaskStatusModel(id=1, title="To Do"),
        TaskStatusModel(id=2, title="In Progress"),
        TaskStatusModel(id=3, title="Done"),
    ]
    db_session.add_all(statuses)

    # Add priorities
    priorities = [
        TaskPriorityModel(id=1, title="High"),
        TaskPriorityModel(id=2, title="Normal"),
        TaskPriorityModel(id=3, title="Low"),
    ]
    db_session.add_all(priorities)

    await db_session.commit()
    yield db_session


@pytest.fixture
async def db_session_with_tasks(db_session_with_data: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with seed data including tasks."""
    now = datetime.now(timezone.utc)
    tasks = [
        TaskModel(
            id=1,
            title="Task 1",
            description="Description 1",
            status_id=1,
            priority_id=1,
            start_time=now,
            end_time=now,
        ),
        TaskModel(
            id=2,
            title="Task 2",
            description=None,
            status_id=2,
            priority_id=2,
            start_time=now,
            end_time=now,
        ),
        TaskModel(
            id=3,
            title="Deleted Task",
            description="This is deleted",
            status_id=1,
            priority_id=1,
            start_time=now,
            end_time=now,
            deleted_at=now,
        ),
    ]
    db_session_with_data.add_all(tasks)
    await db_session_with_data.commit()
    yield db_session_with_data


@pytest.fixture
async def client(async_engine) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with overridden database session."""
    async_session_maker = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with async_session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def client_with_data(async_engine) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with seeded database."""
    async_session_maker = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    # Seed data
    async with async_session_maker() as session:
        statuses = [
            TaskStatusModel(id=1, title="To Do"),
            TaskStatusModel(id=2, title="In Progress"),
            TaskStatusModel(id=3, title="Done"),
        ]
        session.add_all(statuses)

        priorities = [
            TaskPriorityModel(id=1, title="High"),
            TaskPriorityModel(id=2, title="Normal"),
            TaskPriorityModel(id=3, title="Low"),
        ]
        session.add_all(priorities)
        await session.commit()

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with async_session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def client_with_tasks(async_engine) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with seeded database including tasks."""
    async_session_maker = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    # Seed data
    async with async_session_maker() as session:
        statuses = [
            TaskStatusModel(id=1, title="To Do"),
            TaskStatusModel(id=2, title="In Progress"),
            TaskStatusModel(id=3, title="Done"),
        ]
        session.add_all(statuses)

        priorities = [
            TaskPriorityModel(id=1, title="High"),
            TaskPriorityModel(id=2, title="Normal"),
            TaskPriorityModel(id=3, title="Low"),
        ]
        session.add_all(priorities)

        now = datetime.now(timezone.utc)
        tasks = [
            TaskModel(
                id=1,
                title="Task 1",
                description="Description 1",
                status_id=1,
                priority_id=1,
                start_time=now,
                end_time=now,
            ),
            TaskModel(
                id=2,
                title="Task 2",
                description=None,
                status_id=2,
                priority_id=2,
                start_time=now,
                end_time=now,
            ),
            TaskModel(
                id=3,
                title="Deleted Task",
                description="This is deleted",
                status_id=1,
                priority_id=1,
                start_time=now,
                end_time=now,
                deleted_at=now,
            ),
        ]
        session.add_all(tasks)
        await session.commit()

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with async_session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

