from datetime import datetime

from pydantic import BaseModel


class BaseSchema(BaseModel):
    """Base schema with common config."""

    class Config:
        from_attributes = True


class TaskStatus(BaseSchema):
    id: int
    title: str


class TaskPriority(BaseSchema):
    id: int
    title: str


class TaskBase(BaseModel):
    title: str
    description: str | None = None


class TaskCreate(TaskBase):
    ...


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status_id: int | None = None
    priority_id: int | None = None


class TaskResponse(BaseSchema):
    id: int
    title: str
    description: str | None
    status_id: int
    priority_id: int
    start_time: datetime | None
    end_time: datetime | None
    created_at: datetime
    deleted_at: datetime | None
