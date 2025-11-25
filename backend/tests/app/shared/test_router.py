from typing import Sequence, get_origin

from fastapi.routing import APIRoute

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
                        f"Route '{route.path}' [{','.join(route.methods)}] returns a primitive type: {check_type}."
                    )
                    continue

    error_msg = "The following endpoints return forbidden top-level types (must be Object or None):\n"
    error_msg += "\n".join(invalid_endpoints)

    assert not invalid_endpoints, error_msg
