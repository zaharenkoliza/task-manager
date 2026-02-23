import json
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import TaskPriority as TaskPriorityModel
from app.models import TaskStatus as TaskStatusModel
from app.repositories.base import BaseRepository

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "seeders"


def load_json(filename: str) -> list[dict]:
    path = CONFIG_DIR / filename
    with open(path, encoding="utf-8") as f:
        return json.load(f)


async def seed_statuses(session: AsyncSession) -> None:
    """Seed statuses from JSON file if they don't exist."""
    repo = BaseRepository(TaskStatusModel, session)
    existing_ids = await repo.get_existing_ids()

    for data in load_json("statuses.json"):
        if data["id"] not in existing_ids:
            await repo.create(**data)


async def seed_priorities(session: AsyncSession) -> None:
    repo = BaseRepository(TaskPriorityModel, session)
    existing_ids = await repo.get_existing_ids()

    for data in load_json("priorities.json"):
        if data["id"] not in existing_ids:
            await repo.create(**data)


async def seed_all() -> None:
    """Seed all reference data."""
    async with AsyncSessionLocal() as session:
        await seed_statuses(session)
        await seed_priorities(session)
        await session.commit()
