from typing import Any, Sequence, get_args, get_origin

from fastapi.routing import APIRoute
from pydantic import BaseModel

from app.main import app


def test_endpoints_return_object_or_none():
    """
    Scans all FastAPI application routes to ensure no endpoint returns
    a primitive or sequence type.
    Only Objects (Pydantic Models) or None are allowed.
    """
    invalid_endpoints = []

    for route in app.routes:
        if isinstance(route, APIRoute):
            if not route.path.startswith("/api/v2/"):
                # We only want to check routes under /api/v2/
                continue

            # This returns the unsubscripted version of a type
            # For example, get_origin(List[Tuple[T, T]][int]) is list
            # Returns None if unsupported
            origin = get_origin(route.response_model)

            check_type = origin if origin is not None else route.response_model

            if check_type is not None:
                if isinstance(check_type, type) and issubclass(check_type, Sequence):
                    invalid_endpoints.append(
                        f"Route '{route.name}'/'{route.path}' [{','.join(route.methods)}] returns a Sequence."
                    )
                    continue

                if check_type in (str, int, bool, float, list, tuple, set, dict):
                    invalid_endpoints.append(
                        f"Route '{route.name}'/'{route.path}' [{','.join(route.methods)}] returns a primitive type: {check_type}."
                    )
                    continue

    error_msg = "The following endpoints return forbidden top-level types (must be Object or None):\n"
    error_msg += "\n".join(invalid_endpoints)

    assert not invalid_endpoints, error_msg


def test_no_old_names_in_request_or_response_schemas():
    """
    Scans all FastAPI application routes to ensure that no key in the request
    or response body contains the key 'dataset' or `data_output`
    """
    invalid_keys = []
    visited_types = set()

    old_names = ["data_output", "dataset"]

    def check_type(type_: Any, context: str):
        if type_ in visited_types:
            return

        visited_types.add(type_)

        # Check if the current type is something like typing.List[T], or typing.Optional[T].
        # We need to check the inner type
        origin = get_origin(type_)
        if origin:
            for arg in get_args(type_):
                check_type(arg, context)
            return

        # Check if type is a Pydantic model, that we can check
        if isinstance(type_, type) and issubclass(type_, BaseModel):
            for name, field in type_.model_fields.items():  # type: ignore[attr-defined]
                for old_name in old_names:
                    if old_name in name.lower():
                        invalid_keys.append(f"{context} -> field '{name}'")
                    check_type(field.annotation, f"{context}.{name}")

    for route in app.routes:
        if not route.path.startswith("/api/v2/"):
            # We only want to check routes under /api/v2/
            continue
        if isinstance(route, APIRoute):
            # Check Response
            if route.response_model:
                check_type(
                    route.response_model,
                    f"Route '{route.name}'/'{route.path}' [Response]",
                )

            # Check Request Body
            if route.body_field:
                # type_to_check = getattr(route.body_field, "annotation", None) or route.body_field.type_
                check_type(
                    route.body_field.type_,
                    f"Route '{route.name}'/'{route.path}' [Request Body]",
                )

    error_msg = "The following routes contain 'dataset' or 'data_output' in request or response keys:\n"
    error_msg += "\n".join(invalid_keys)

    assert not invalid_keys, error_msg


def test_no_old_names_in_url():
    """
    Scans all FastAPI application routes to ensure that no key in the request
    or response body contains the key 'dataset' or `data_output`
    """

    old_names = ["data_output", "dataset"]

    def route_path_contains_old_name(path: str):
        return any(old_name in path for old_name in old_names)

    invalid_routes = [
        f"- '{route.name}'/'{route.path}'"
        for route in app.routes
        if route.path.startswith("/api/v2/")
        and route_path_contains_old_name(route.path)
    ]

    error_msg = "The following routes contain 'dataset' or 'data_output' in the URL:\n"
    error_msg += "\n".join(invalid_routes)

    assert not invalid_routes, error_msg
