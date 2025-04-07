from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from app.services.task_scheduler import TaskScheduler, get_task_scheduler, TaskMetadata

task_router = APIRouter(prefix="/tasks")

TaskSchedulerDep = Annotated[TaskScheduler, Depends(get_task_scheduler)]


@task_router.get("")
async def get_tasks(task_scheduler: TaskSchedulerDep) -> dict[str, TaskMetadata]:
    return dict(
        [(task_id, task.metadata) for task_id, task in task_scheduler.tasks.items()]
    )


@task_router.post("", status_code=201)
async def add_task(task_metadata: TaskMetadata, task_scheduler: TaskSchedulerDep):
    if task_scheduler.has_task(task_metadata.name):
        raise HTTPException(status_code=419, detail="Task name is taken")

    await task_scheduler.add_task(task_metadata)


@task_router.delete("")
async def clear_tasks(task_scheduler: TaskSchedulerDep):
    for task in list(task_scheduler.tasks.keys()):
        await task_scheduler.remove_task(task)


@task_router.delete("/{task_name}")
async def delete_task(task_name: str, task_scheduler: TaskSchedulerDep):
    if not task_scheduler.has_task(task_name):
        raise HTTPException(status_code=404, detail="Task not found")

    await task_scheduler.remove_task(task_name)
