from typing import Optional, Type, get_args, get_origin

from fastapi import FastAPI
from pydantic import BaseModel

from app.main import app as f_app


def test_export_openapi() -> None:
    collisions = find_model_name_collisions(f_app)
    assert len(collisions) == 0, collision_message(collisions)


def find_model_name_collisions(app: FastAPI) -> dict[str, list[Type]]:
    # Collect all models used in the application
    unique_models: set[Type] = set()

    # Extract request and response models from all routes
    for route in app.routes:
        # Check Response Model
        if hasattr(route, "response_model"):
            extract_models(route.response_model, unique_models)

        # Check Request Body Models
        if hasattr(route, "dependant"):
            for dep in route.dependant.body_params:
                extract_models(dep.type_, unique_models)

    # Group by class name
    name_map: dict[str, list[Type]] = {}
    for model in unique_models:
        name = model.__name__
        if name not in name_map:
            name_map[name] = []
        name_map[name].append(model)

    # Report collisions
    collisions = {k: v for k, v in name_map.items() if len(v) > 1}
    return collisions


def extract_models(type_annotation: Optional[Type], found_models: set[Type]) -> None:
    """
    Recursively extracts Pydantic models from generics (List, Union, etc.)
    """
    if type_annotation is None:
        return

    # 1. If it's a Pydantic Model, add it
    # We check issubclass, but we must ensure it's actually a class first
    # to avoid TypeError on instances like 'List[int]'
    try:
        if isinstance(type_annotation, type) and issubclass(type_annotation, BaseModel):
            found_models.add(type_annotation)
            return
    except TypeError:
        pass  # It was not a class (e.g. it was a typing object), continue to check args

    # 2. If it's a Generic (List[T], Union[A, B]), recurse into its arguments
    # get_origin returns the base type (e.g., list, Union)
    # get_args returns the contents (e.g., (User,))
    get_origin(type_annotation)
    args = get_args(type_annotation)

    if args:
        for arg in args:
            extract_models(arg, found_models)


def collision_message(collisions: dict) -> str:
    msg = f"Found {len(collisions)} model name collisions: "
    for name, models in collisions.items():
        msg += f"Name: '{name}'"
        for m in models:
            msg += f"  - {m.__module__}.{m.__name__}"
    return msg
