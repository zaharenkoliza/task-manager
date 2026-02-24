from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Task as TaskModel
from app.models import TaskPriority as TaskPriorityModel
from app.models import TaskStatus as TaskStatusModel
from app.repositories import TaskRepository
from app.repositories.base import BaseRepository
from app.schemas import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
        session: AsyncSession = Depends(get_session),
        status_id: int | None = Query(None),
        priority_id: int | None = Query(None),
        start_time: datetime | None = Query(None),
        end_time: datetime | None = Query(None),
) -> list[TaskModel]:
    repo = TaskRepository(session)
    return list(await repo.get_multi(
        status_id=status_id,
        priority_id=priority_id,
        start_time=start_time,
        end_time=end_time,
    ))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, session: AsyncSession = Depends(get_session)) -> TaskModel:
    """Get a single task by id."""
    repo = TaskRepository(session)
    task = await repo.get_single(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(body: TaskCreate, session: AsyncSession = Depends(get_session)) -> TaskModel:
    """Create a new task."""
    status_repo = BaseRepository(TaskStatusModel, session)
    priority_repo = BaseRepository(TaskPriorityModel, session)
    task_repo = TaskRepository(session)

    # Get default status (first one)
    statuses = await status_repo.get_all()
    if not statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No statuses available",
        )
    default_status = statuses[0]

    # Get default priority (second one = Normal, or first if only one)
    priorities = await priority_repo.get_all()
    if not priorities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No priorities available",
        )
    default_priority = priorities[1] if len(priorities) > 1 else priorities[0]

    task = await task_repo.create(
        title=body.title,
        description=body.description,
        status_id=default_status.id,
        priority_id=default_priority.id,
    )
    await session.commit()
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
        task_id: int, body: TaskUpdate, session: AsyncSession = Depends(get_session)
) -> TaskModel:
    """Update an existing task."""
    task_repo = TaskRepository(session)
    status_repo = BaseRepository(TaskStatusModel, session)
    priority_repo = BaseRepository(TaskPriorityModel, session)

    task = await task_repo.get_single(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    update_data = body.model_dump(exclude_unset=True)

    # Validate status_id if provided
    if "status_id" in update_data:
        if not await status_repo.exists(update_data["status_id"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status_id",
            )

    # Validate priority_id if provided
    if "priority_id" in update_data:
        if not await priority_repo.exists(update_data["priority_id"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid priority_id",
            )

    task = await task_repo.update(task_id, **update_data)
    await session.commit()
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, session: AsyncSession = Depends(get_session)) -> None:
    """Soft delete a task."""
    repo = TaskRepository(session)
    deleted = await repo.soft_delete(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    await session.commit()
