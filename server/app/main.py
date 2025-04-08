from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.utils.actions import get_actions
from .routers import tasks, devices

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"name": "ampi-server", "version": "{{version}}"}


@app.get("/actions")
async def list_actions() -> list[str]:
    return get_actions()


app.router.include_router(tasks.task_router)
app.router.include_router(devices.devices_router)
