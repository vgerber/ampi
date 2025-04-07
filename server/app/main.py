from fastapi import FastAPI

from app.utils.actions import get_actions
from .routers import tasks

app = FastAPI()


@app.get("/")
async def root():
    return {"name": "ampi-server", "version": "{{version}}"}


@app.get("/actions")
async def list_actions() -> list[str]:
    return get_actions()


app.router.include_router(tasks.task_router)
