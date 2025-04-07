from multiprocessing import Process
from typing import Annotated, Callable
from pydantic import BaseModel, Field

from app.actions.print_hello import run
import asyncio


class TaskMetadata(BaseModel):
    name: Annotated[str, Field(default="task", description="Name of task")]
    action: Annotated[str, Field(description="Name of action")]
    arguments: Annotated[dict, Field(default=dict(), description="Action arguments")]


class Task:
    def __init__(self, metadata: TaskMetadata):
        self.metadata = metadata
        self.task = asyncio.create_task(
            self._run_action(metadata.action, metadata.arguments)
        )

    async def _run_action(self, action: str, arguments: dict):
        await run(**arguments)


class TaskScheduler:
    def __init__(self):
        self.tasks_lock = asyncio.Lock()
        self.tasks: dict[str, Task] = dict()

    def has_task(self, task_name: str) -> bool:
        return task_name in self.tasks

    async def add_task(self, task_metadata: TaskMetadata):
        async with self.tasks_lock:
            task = Task(
                metadata=task_metadata,
            )
            task.task.add_done_callback(
                lambda _: asyncio.create_task(self.remove_task(task_metadata.name))
            )
            self.tasks[task_metadata.name] = task

    async def remove_task(self, task_name: str):
        async with self.tasks_lock:
            if not self.has_task(task_name):
                return
            task = self.tasks[task_name].task
            if not task.done():
                task.cancel()
            del self.tasks[task_name]


_task_scheduler = TaskScheduler()


def get_task_scheduler() -> TaskScheduler:
    return _task_scheduler
