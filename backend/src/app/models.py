from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TaskStatus(Base):
    __tablename__ = "task_statuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    tasks: Mapped[list["Task"]] = relationship(back_populates="status")


class TaskPriority(Base):
    __tablename__ = "task_priorities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    tasks: Mapped[list["Task"]] = relationship(back_populates="priority")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    status_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("task_statuses.id", ondelete="RESTRICT"), nullable=False
    )
    priority_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("task_priorities.id", ondelete="RESTRICT"), nullable=False
    )

    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    status: Mapped[TaskStatus] = relationship(back_populates="tasks")
    priority: Mapped[TaskPriority] = relationship(back_populates="tasks")
