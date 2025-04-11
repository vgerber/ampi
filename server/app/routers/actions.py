from app.utils.actions import get_action_model, get_actions
from fastapi import APIRouter


actions_router = APIRouter(prefix="/actions")


@actions_router.get("")
async def list_actions() -> list[str]:
    return get_actions()


@actions_router.get("/{action}/schema", operation_id="get_action_model")
async def get_action_model_endpoint(action: str) -> dict:
    return get_action_model(action).model_json_schema()
