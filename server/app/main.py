from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from .routers import tasks, devices, actions

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


app.router.include_router(tasks.task_router)
app.router.include_router(devices.devices_router)
app.router.include_router(actions.actions_router)
