from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import TaskPriority as TaskPriorityModel
from app.repositories.base import BaseRepository
from app.schemas import TaskPriority

router = APIRouter(prefix="/tasks/priorities", tags=["task_priorities"])


@router.get("", response_model=list[TaskPriority])
async def list_priorities(session: AsyncSession = Depends(get_session)) -> list[TaskPriorityModel]:
    """Get all task priorities."""
    repo = BaseRepository(TaskPriorityModel, session)
    return list(await repo.get_all())


@router.get("/{priority_id}", response_model=TaskPriority)
async def get_priority(priority_id: int, session: AsyncSession = Depends(get_session)) -> TaskPriorityModel:
    """Get a single task priority by id."""
    repo = BaseRepository(TaskPriorityModel, session)
    priority_obj = await repo.get_single(priority_id)
    if not priority_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Priority not found",
        )
    return priority_obj
