"""Tasks endpoint."""
from fastapi import APIRouter, Depends
from app.api.schemas import TaskListResponse, TaskInfo
from app.dependencies import get_task_registry

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=TaskListResponse, summary="List all available tasks")
async def list_tasks(registry=Depends(get_task_registry)):
    tasks = [TaskInfo(**t) for t in registry.list_all()]
    return TaskListResponse(tasks=tasks)
