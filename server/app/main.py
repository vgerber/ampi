from fastapi import FastAPI
from .routers import tasks

app = FastAPI()


@app.get("/")
async def root():
    return {"name": "ampi-server", "version": "{{version}}"}


app.router.include_router(tasks.task_router)
