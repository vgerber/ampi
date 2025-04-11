from importlib import import_module
import os
import pkgutil
from typing import Callable
import app.actions
from pydantic import BaseModel, create_model
from inspect import signature


def get_actions() -> list[str]:
    pkg_path = os.path.dirname(app.actions.__file__)
    return [module_info.name for module_info in pkgutil.iter_modules([pkg_path])]


def get_action_callable(action: str) -> Callable:
    module = import_module(package="app.actions", name=f".{action}")
    return getattr(module, "run")


def get_action_model(action: str) -> BaseModel:
    run_callable: Callable = get_action_callable(action)
    run_callable_signature = signature(run_callable)

    parameters = [
        (name, param)
        for name, param in run_callable_signature.parameters.items()
        if name != "device"
    ]

    return create_model(
        f"{action}_model",
        **{
            name: (
                param.annotation,
                param.default if param.default is not param.empty else ...,
            )
            for name, param in parameters
        },
    )
