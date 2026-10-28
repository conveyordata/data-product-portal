from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute

from app.database.database import get_system_db_session
from app.database.deps import get_db_session
from app.main import app
from app.open_api_export import custom_openapi


def test_endpoints_return_object_or_none():
    """
    Scans all FastAPI application routes via the OpenAPI spec to ensure no endpoint
    returns a primitive or array type at the top level.
    Only Objects (Pydantic Models) or None are allowed.
    """
    openapi_schema = custom_openapi(app)
    invalid_endpoints = []

    primitive_types = {"string", "integer", "number", "boolean", "null"}

    for path, path_item in openapi_schema.get("paths", {}).items():
        for method, operation in path_item.items():
            for response in operation.get("responses", {}).values():
                for media_type_obj in response.get("content", {}).values():
                    schema = media_type_obj.get("schema")
                    if not isinstance(schema, dict):
                        continue

                    schema_type = schema.get("type")
                    if schema_type == "array" or schema_type in primitive_types:
                        invalid_endpoints.append(
                            f"Route '{method.upper()} {path}' returns forbidden top-level schema type: {schema_type}."
                        )

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


def test_openapi_file_upload_uses_binary_schema():
    path = (
        "/api/v2/data_products/{data_product_id}/output_ports/{id}/data_contract/upload"
    )
    schema = custom_openapi(app)["paths"][path]["post"]["requestBody"]["content"][
        "multipart/form-data"
    ]["schema"]["properties"]["file"]

    assert schema == {
        "type": "string",
        "format": "binary",
        "title": "File",
    }


def _iter_app_routes():
    def walk(node):
        if isinstance(node, APIRoute):
            yield node
            return

        if type(node).__name__ == "_IncludedRouter":
            for candidate in node.effective_candidates():
                yield from walk(candidate)
            return

        if hasattr(node, "path") and hasattr(node, "dependencies"):
            yield node

    for route in app.routes:
        yield from walk(route)


def _route_has_authorization_enforce(route) -> bool:
    dependencies = list(getattr(route, "dependencies", []) or [])
    dependencies.extend(getattr(route.dependant, "dependencies", []) or [])

    for dependency in dependencies:
        call = getattr(dependency, "call", None)
        if call is None:
            continue

        qualname = getattr(call, "__qualname__", "")
        module = getattr(call, "__module__", "")
        name = getattr(call, "__name__", "")

        if (
            "Authorization.enforce" in qualname
            or "Authorization.enforce" in repr(call)
            or qualname.startswith("Authorization.enforce.<locals>.inner")
            or (name == "inner" and qualname.startswith("Authorization.enforce."))
            or (
                module.startswith("app.")
                and qualname.startswith("Authorization.enforce.")
            )
        ):
            return True

    return False


def _iter_dependants(dependant: Dependant):
    yield dependant
    for dependency in dependant.dependencies:
        yield from _iter_dependants(dependency)


def test_every_protected_v2_route_has_authorization_enforce_dependency():
    excluded_paths = {
        # Everyone is allowed to read the list of data products, so no authorization is needed.
        # We filter out hidden data products in the service layer
        "/api/v2/data_products",
    }
    missing = []

    for route in _iter_app_routes():
        if not getattr(route, "path", "").startswith("/api/v2/"):
            continue
        # We only check data products paths
        if not route.path.startswith("/api/v2/data_products"):
            continue
        if route.path in excluded_paths:
            continue

        if not _route_has_authorization_enforce(route):
            missing.append(f"{route.path} [{route.name}]")

    assert not missing, (
        "The following API routes do not declare an Authorization.enforce dependency:\n"
        + "\n".join(missing)
    )


def test_db_session_dependencies_use_function_scope():
    invalid = []

    for route in _iter_app_routes():
        for dependant in _iter_dependants(route.dependant):
            call = getattr(dependant, "call", None)
            if call not in {get_db_session, get_system_db_session}:
                continue
            if getattr(dependant, "scope", None) != "function":
                invalid.append(
                    f"{route.path} [{route.name}] uses {call.__name__} without scope='function'"
                )

    assert not invalid, (
        "The following API routes use database session dependencies without "
        "scope='function':\n" + "\n".join(invalid)
    )


def test_routes_only_use_get_db_session():
    exceptions = [
        # Device flow routs don't need an authenticated session, since the user is unauthenticated at this point.
        "/api/v2/authn/device/device_token",
        "/api/v2/authn/device/jwt_token",
        "/api/v2/authn/device",
        "/api/v2/authn/device/deny",
        "/api/v2/authn/device/allow",
        "/api/v2/authn/device/callback",
    ]

    invalid = []

    for route in _iter_app_routes():
        if route.path in exceptions:
            continue
        direct_calls = {
            getattr(dependant, "call", None)
            for dependant in getattr(route.dependant, "dependencies", []) or []
        }

        if get_system_db_session in direct_calls:
            invalid.append(
                f"{route.path} [{route.name}] uses get_system_db_session directly"
            )

    assert not invalid, (
        "The following API routes use get_system_db_session directly instead of "
        "get_db_session:\n" + "\n".join(invalid)
    )


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
