from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import TaskStatus as TaskStatusModel
from app.repositories.base import BaseRepository
from app.schemas import TaskStatus

router = APIRouter(prefix="/tasks/statuses", tags=["task_statuses"])


@router.get("", response_model=list[TaskStatus])
async def list_statuses(session: AsyncSession = Depends(get_session)) -> list[TaskStatusModel]:
    """Get all task statuses."""
    repo = BaseRepository(TaskStatusModel, session)
    return list(await repo.get_all())


@router.get("/{status_id}", response_model=TaskStatus)
async def get_status(status_id: int, session: AsyncSession = Depends(get_session)) -> TaskStatusModel:
    """Get a single task status by id."""
    repo = BaseRepository(TaskStatusModel, session)
    status_obj = await repo.get_single(status_id)
    if not status_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Status not found",
        )
    return status_obj
