from datetime import datetime, timezone
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task as TaskModel
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[TaskModel]):
    """Repository for Task with soft delete support."""

    def __init__(self, session: AsyncSession):
        super().__init__(TaskModel, session)

    async def get_single(self, id: int) -> TaskModel | None:
        """Get single non-deleted task by id."""
        result = await self.session.execute(
            select(self.model).where(
                self.model.id == id,
                self.model.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_multi(
            self,
            *,
            offset: int = 0,
            limit: int = 100,
            order_by: Any = None,
            status_id: int | None = None,
            priority_id: int | None = None,
            start_time: datetime | None = None,
            end_time: datetime | None = None,
    ) -> Sequence[TaskModel]:
        """Get multiple non-deleted tasks with filters."""
        query = select(self.model).where(self.model.deleted_at.is_(None))

        if status_id is not None:
            query = query.where(self.model.status_id == status_id)
        if priority_id is not None:
            query = query.where(self.model.priority_id == priority_id)
        if start_time is not None:
            query = query.where(self.model.start_time >= start_time)
        if end_time is not None:
            query = query.where(self.model.end_time <= end_time)

        if order_by is not None:
            query = query.order_by(order_by)
        else:
            query = query.order_by(self.model.id)

        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def soft_delete(self, id: int) -> bool:
        """Soft delete task by id. Returns True if deleted."""
        task = await self.get_single(id)
        if not task:
            return False

        task.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()
        return True
