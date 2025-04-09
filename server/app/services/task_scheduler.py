from importlib import import_module
from typing import Annotated
from app.services.devices_service import DeviceData, DevicesService
from pydantic import BaseModel, Field

import asyncio


class TaskMetadata(BaseModel):
    name: Annotated[str, Field(default="task", description="Name of task")]
    device_name: Annotated[str, Field(description="Name of device")]
    action: Annotated[str, Field(description="Name of action")]
    arguments: Annotated[dict, Field(default=dict(), description="Action arguments")]


class Task:
    def __init__(self, metadata: TaskMetadata, device: DeviceData):
        self.metadata = metadata
        self.task = asyncio.create_task(
            self._run_action(device, metadata.action, metadata.arguments)
        )

    async def _run_action(self, device: DeviceData, action: str, arguments: dict):
        try:
            module = import_module(package="app.actions", name=f".{action}")
            await getattr(module, "run")(device, **arguments)
        except Exception as ex:
            print(ex)


class TaskScheduler:
    def __init__(self):
        self.tasks_lock = asyncio.Lock()
        self.tasks: dict[str, Task] = dict()

    def has_task(self, task_name: str) -> bool:
        return task_name in self.tasks

    async def add_task(self, device: DeviceData, task_metadata: TaskMetadata):
        async with self.tasks_lock:
            task = Task(
                device=device,
                metadata=task_metadata,
            )
            task.task.add_done_callback(
                lambda _: asyncio.create_task(self.remove_task(task_metadata.name))
            )
            self.tasks[task_metadata.name] = task

    async def remove_task(self, task_name: str):
        print(f"{task_name} completed")
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
