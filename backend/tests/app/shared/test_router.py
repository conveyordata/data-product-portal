from typing import Sequence, get_origin

from fastapi.dependencies.models import Dependant
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
                        f"Route '{route.name}'/'{route.path}' [{','.join(route.methods)}] returns a primitive type: {check_type}."
                    )
                    continue

    error_msg = "The following endpoints return forbidden top-level types (must be Object or None):\n"
    error_msg += "\n".join(invalid_endpoints)

    assert not invalid_endpoints, error_msg


def test_no_old_names_in_request_or_response_schemas():
    """
    Scans all FastAPI application routes via the OpenAPI spec to ensure that no
    key in the request or response body contains 'dataset' or 'data_output'.
    """
    openapi_schema = app.openapi()
    paths = openapi_schema.get("paths", {})
    schemas = openapi_schema.get("components", {}).get("schemas", {})

    invalid_keys = []
    old_names = ["data_output", "dataset"]
    visited_schemas = set()

    def check_schema(schema_dict: dict, context: str):
        if not isinstance(schema_dict, dict):
            return

        if "$ref" in schema_dict:
            ref_name = schema_dict["$ref"].split("/")[-1]
            if ref_name in visited_schemas:
                return
            visited_schemas.add(ref_name)
            schema_dict = schemas.get(ref_name, {})

        properties = schema_dict.get("properties", {})
        for prop_name, prop_val in properties.items():
            if any(old_name in prop_name.lower() for old_name in old_names):
                invalid_keys.append(f"{context} -> field '{prop_name}'")

            check_schema(prop_val, f"{context}.{prop_name}")

        if schema_dict.get("type") == "array" and "items" in schema_dict:
            check_schema(schema_dict["items"], context)

        for combiner in ["anyOf", "allOf", "oneOf"]:
            if combiner in schema_dict:
                for sub_schema in schema_dict[combiner]:
                    check_schema(sub_schema, context)

    for path, path_item in paths.items():
        if not path.startswith("/api/v2/"):
            continue

        for method, operation in path_item.items():
            if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                continue

            context_prefix = f"Route '{method.upper()} {path}'"

            request_body = operation.get("requestBody", {})
            content = request_body.get("content", {})
            for media_type_obj in content.values():
                if "schema" in media_type_obj:
                    check_schema(
                        media_type_obj["schema"], f"{context_prefix} [Request Body]"
                    )

            responses = operation.get("responses", {})
            for status_code, response_obj in responses.items():
                resp_content = response_obj.get("content", {})
                for media_type_obj in resp_content.values():
                    if "schema" in media_type_obj:
                        check_schema(
                            media_type_obj["schema"],
                            f"{context_prefix} [Response {status_code}]",
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
        return any(old_name in path.lower() for old_name in old_names)

    paths = app.openapi().get("paths", {})
    invalid_routes = [
        path
        for path in paths
        if path.startswith("/api/v2/") and route_path_contains_old_name(path)
    ]

    error_msg = "The following routes contain 'dataset' or 'data_output' in the URL:\n"
    error_msg += "\n".join(invalid_routes)

    assert not invalid_routes, error_msg


def test_no_token_in_route_params():
    def get_all_query_param_names(dependant: Dependant) -> set:
        param_names = {param.name for param in dependant.query_params}
        for sub_dependant in dependant.dependencies:
            param_names.update(get_all_query_param_names(sub_dependant))
        return param_names

    routes_with_token = [
        f"{route.path} [{route.name}]"
        for route in app.routes
        if isinstance(route, APIRoute)
        and "token" in get_all_query_param_names(route.dependant)
    ]

    assert not routes_with_token, (
        f"Found unwanted 'token' query parameter in the following routes: {routes_with_token}"
    )


def test_openapi_no_duplicate_operation_ids():
    openapi_schema = app.openapi()
    operation_ids = set()
    duplicates = set()

    for methods in openapi_schema.get("paths", {}).values():
        for config in methods.values():
            if operation_id := config.get("operationId"):
                if operation_id in operation_ids:
                    duplicates.add(operation_id)
                operation_ids.add(operation_id)

    assert not duplicates, f"Duplicate operationIds found in OpenAPI spec: {duplicates}"


def test_routes_not_v2_are_deprecated():
    """
    Ensures that all routes not starting with /api/v2/ are marked as deprecated.
    """
    # Add paths or route names here to skip this check
    EXCEPTIONS = {
        "/mcp",
    }

    non_deprecated_old_routes = []

    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue

        # Skip exceptions
        if route.path in EXCEPTIONS or route.name in EXCEPTIONS:
            continue

        if not route.path.startswith("/api/v2/") and not route.deprecated:
            non_deprecated_old_routes.append(
                f"Route '{route.name}' ('{route.path}') is not /api/v2/ but is NOT marked as deprecated."
            )

    error_msg = (
        "The following routes are legacy (not /api/v2/) but lack the 'deprecated=True' flag:\n"
        + "\n".join(non_deprecated_old_routes)
    )

    assert not non_deprecated_old_routes, error_msg
