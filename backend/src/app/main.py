from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.config import settings
from app.database import create_tables
from app.models import Task, TaskPriority, TaskStatus  # noqa: F401 - ensure models are loaded
from app.routers import priorities, statuses, tasks
from app.seed import seed_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    await seed_all()
    yield


app = FastAPI(
    title="Task Manager API",
    description="REST API for managing tasks.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(statuses.router, prefix="/api")
app.include_router(priorities.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.debug)
