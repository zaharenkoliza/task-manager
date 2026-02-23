from typing import Any, Generic, Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Universal repository for database operations."""

    def __init__(self, model: type[ModelT], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_single(self, id: int) -> ModelT | None:
        """Get single record by id."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi(
            self,
            *,
            offset: int = 0,
            limit: int = 100,
            order_by: Any = None,
            **filters: Any,
    ) -> Sequence[ModelT]:
        """Get multiple records with optional filters, pagination and ordering."""
        query = select(self.model)

        for field, value in filters.items():
            if value is not None:
                query = query.where(getattr(self.model, field) == value)

        if order_by is not None:
            query = query.order_by(order_by)
        else:
            query = query.order_by(self.model.id)

        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all(self, *, order_by: Any = None) -> Sequence[ModelT]:
        """Get all records."""
        query = select(self.model)

        if order_by is not None:
            query = query.order_by(order_by)
        else:
            query = query.order_by(self.model.id)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, **data: Any) -> ModelT:
        """Create a new record."""
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: int, **data: Any) -> ModelT | None:
        """Update record by id."""
        instance = await self.get_single(id)
        if not instance:
            return None

        for field, value in data.items():
            setattr(instance, field, value)

        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: int) -> bool:
        """Delete record by id. Returns True if deleted."""
        instance = await self.get_single(id)
        if not instance:
            return False

        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def exists(self, id: int) -> bool:
        """Check if record exists."""
        instance = await self.get_single(id)
        return instance is not None

    async def get_existing_ids(self) -> set[int]:
        """Get set of all existing ids."""
        result = await self.session.execute(select(self.model.id))
        return {row[0] for row in result.all()}

    async def create_if_not_exists(self, id: int, **data: Any) -> ModelT | None:
        """Create record only if id doesn't exist. Returns created instance or None."""
        if await self.exists(id):
            return None
        return await self.create(id=id, **data)
