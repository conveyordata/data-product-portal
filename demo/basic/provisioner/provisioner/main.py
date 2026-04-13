import logging
import re
import os
from cookiecutter.main import cookiecutter
from fastapi import FastAPI, Request
from typing import Callable, List, Tuple, Dict, Any
import json
from uuid import UUID

from sdk import Client
from sdk.api_client.api.configuration_data_product_lifecycles import (
    get_data_products_lifecycles,
)
from sdk.api_client.api.configuration_platforms import (
    get_all_platform_service_configurations,
)
from sdk.api_client.api.data_products import get_data_product, update_data_product
from sdk.api_client.api.data_products_technical_assets import (
    create_technical_asset,
    update_technical_asset_status,
)
from sdk.api_client.models import (
    DataProductUpdate,
    CreateTechnicalAssetRequest,
    DataOutputStatusUpdate,
    HTTPValidationError,
)
from sdk.api_client.models.technical_asset_status import TechnicalAssetStatus
from sdk.api_client.models.technical_mapping import TechnicalMapping
from sdk.api_client.models.postgre_sql_technical_asset_configuration import (
    PostgreSQLTechnicalAssetConfiguration,
)
from sdk.api_client.models.access_granularity import AccessGranularity

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# get the namespace of the data product
portal_url = os.environ.get("PROV_DPP_API_URL", "http://localhost:80801")

# SDK client (no auth needed — demo runs with OIDC_ENABLED=false)
client = Client(base_url=portal_url)

# Calculate base directories relative to this script
# Script is at demo/basic/provisioner/provisioner/main.py
script_dir = os.path.dirname(os.path.abspath(__file__))
provisioner_dir = os.path.dirname(script_dir)  # demo/basic/provisioner
basic_demo_dir = os.path.dirname(provisioner_dir)  # demo/basic

template_path = os.environ.get(
    "PROV_TEMPLATE_PATH",
    os.path.join(provisioner_dir, "templates", "dbt"),
)
tempplate_output_path = os.environ.get(
    "PROV_TEMPLATE_OUTPUT_PATH",
    os.path.join(basic_demo_dir, "products"),
)

# In-memory cache for data product lifecycles
lifecycle_cache: Dict[str, Any] = {}

# In-memory cache for platform service configurations
platform_service_configurations_cache: Dict[str, Any] = {}


# --- Route Handlers ---
# These are example functions that will be called when a route matches.
# They can be moved to different files as the application grows.


def get_lifecycles() -> List[Any]:
    """
    Fetches data product lifecycles from the API, with in-memory caching.
    """
    global lifecycle_cache
    if "lifecycles" in lifecycle_cache:
        logging.info("Returning cached lifecycles")
        return lifecycle_cache["lifecycles"]

    logging.info("Fetching lifecycles from portal API")
    result = get_data_products_lifecycles.sync(client=client)

    if result is None:
        logging.error("Failed to fetch lifecycles: no response")
        return []

    lifecycles = result.data_product_life_cycles
    lifecycle_cache["lifecycles"] = lifecycles
    logging.info(f"Successfully fetched and cached {len(lifecycles)} lifecycles")
    return lifecycles


def get_platform_service_configurations() -> List[Any]:
    """
    Fetches platform service configurations from the API, with in-memory caching.
    """
    global platform_service_configurations_cache
    if "platform_service_configurations" in platform_service_configurations_cache:
        logging.info("Returning cached platform service configurations")
        return platform_service_configurations_cache["platform_service_configurations"]

    logging.info("Fetching platform service configurations from portal API")
    result = get_all_platform_service_configurations.sync(client=client)

    if result is None:
        logging.error("Failed to fetch platform service configurations: no response")
        return []

    configs = result.platform_service_configurations
    platform_service_configurations_cache["platform_service_configurations"] = configs
    logging.info(
        f"Successfully fetched and cached {len(configs)} platform service configurations"
    )
    return configs


def handle_create_data_product(payload: Dict[str, Any]):
    """Handler for creating a data product."""
    logging.info(f"Creating data product with payload: {payload}")

    response_data = json.loads(payload.get("response", "{}"))
    data_product_id = response_data.get("id")

    if not data_product_id:
        logging.error("Could not find data product id in response")
        return {
            "status": "error",
            "message": "Could not find data product id in response",
        }

    # Fetch data product details
    data_product_details = get_data_product.sync(
        id=UUID(data_product_id), client=client
    )
    if data_product_details is None or isinstance(
        data_product_details, HTTPValidationError
    ):
        logging.error(f"Failed to get data product details for id {data_product_id}")
        return {
            "status": "error",
            "message": f"Failed to get data product details for id {data_product_id}",
        }

    namespace = data_product_details.namespace
    logging.info(f"Data product namespace: {namespace}")

    # call the cookiecutter template
    context = {"project_name": namespace}
    cookiecutter(
        template_path,
        no_input=True,
        extra_context=context,
        output_dir=tempplate_output_path,
    )

    # get the lifecycles and find the "Ready" state
    lifecycles = get_lifecycles()
    ready_lifecycle = next((lc for lc in lifecycles if lc.name == "Ready"), None)

    if not ready_lifecycle:
        logging.error("Could not find 'Ready' lifecycle state.")
        return {
            "status": "error",
            "message": "Configuration error: 'Ready' lifecycle not found.",
        }

    # Update the data product to the "Ready" state
    update_body = DataProductUpdate(
        name=data_product_details.name,
        namespace=data_product_details.namespace,
        description=data_product_details.description,
        type_id=data_product_details.type_.id,
        lifecycle_id=ready_lifecycle.id,
        domain_id=data_product_details.domain.id,
        tag_ids=[tag.id for tag in data_product_details.tags],
    )

    logging.info(f"Updating data product {data_product_id} to 'Ready' state")
    update_result = update_data_product.sync(
        id=UUID(data_product_id), body=update_body, client=client
    )

    if update_result is None:
        logging.error(f"Failed to update data product state for id {data_product_id}")
        return {
            "status": "error",
            "message": f"Failed to update data product state for id {data_product_id}",
        }

    logging.info(
        f"Successfully updated data product {data_product_id} to 'Ready' state."
    )

    # Create the data output port
    configs = get_platform_service_configurations()
    postgres_config = next((c for c in configs if c.service.name == "PostgreSQL"), None)

    if not postgres_config:
        logging.error("Could not find 'PostgreSQL' service configuration.")
        return {
            "status": "error",
            "message": "Configuration error: 'PostgreSQL' service not found.",
        }

    schema_name = data_product_details.namespace.replace("-", "_")

    configuration = PostgreSQLTechnicalAssetConfiguration(
        configuration_type="PostgreSQLTechnicalAssetConfiguration",
        database="dpp_demo",
        schema=schema_name,
        access_granularity=AccessGranularity.SCHEMA,
        table="*",
    )

    technical_asset_body = CreateTechnicalAssetRequest(
        name=data_product_details.name,
        namespace=data_product_details.namespace,
        description=data_product_details.description,
        tag_ids=[],
        status=TechnicalAssetStatus.ACTIVE,
        technical_mapping=TechnicalMapping.CUSTOM,
        platform_id=postgres_config.platform.id,
        service_id=postgres_config.service.id,
        configuration=configuration,
    )

    technical_asset_url = (
        f"{portal_url}/api/v2/data_products/{data_product_id}/technical_assets"
    )
    logging.info(f"Creating technical asset at {technical_asset_url}")

    technical_asset_result = create_technical_asset.sync(
        data_product_id=UUID(data_product_id),
        body=technical_asset_body,
        client=client,
    )

    if technical_asset_result is None or isinstance(
        technical_asset_result, HTTPValidationError
    ):
        logging.error(f"Failed to create technical asset for id {data_product_id}")
        return {
            "status": "error",
            "message": f"Failed to create technical asset for id {data_product_id}",
        }

    technical_asset_id = technical_asset_result.id
    logging.info(
        f"Successfully created technical asset {technical_asset_id} for data product {data_product_id}."
    )

    # Set technical asset status to active
    status_response = update_technical_asset_status.sync_detailed(
        data_product_id=UUID(data_product_id),
        id=technical_asset_id,
        body=DataOutputStatusUpdate.from_dict(
            {"status": TechnicalAssetStatus.ACTIVE.value}
        ),
        client=client,
    )

    if status_response.status_code != 200:
        logging.error(
            f"Failed to set technical asset {technical_asset_id} status to active"
        )
        # Don't return error here because the asset was at least created
    else:
        logging.info(
            f"Successfully set technical asset {technical_asset_id} status to active."
        )

    return {
        "status": "success",
        "action": "create_data_product",
        "original_response": json.loads(payload.get("response", "{}")),
    }


def handle_approve_link(
    data_product_id: str, output_port_id: str, payload: Dict[str, Any]
):
    """Handler for approving a data product link."""
    logging.info(
        f"Approving link for data_product={data_product_id} output_port={output_port_id} with payload: {payload}"
    )
    return {
        "status": "success",
        "action": "approve_link",
        "data_product_id": data_product_id,
        "output_port_id": output_port_id,
    }


def handle_update_data_product(product_id: str, payload: Dict[str, Any]):
    """Handler for updating a data product."""
    logging.info(f"Updating data product {product_id} with payload: {payload}")
    return {
        "status": "success",
        "action": "update_data_product",
        "product_id": product_id,
    }


def handle_delete_data_product(product_id: str, payload: Dict[str, Any]):
    """Handler for deleting a data product."""
    logging.info(f"Deleting data product {product_id} with payload: {payload}")
    return {
        "status": "success",
        "action": "delete_data_product",
        "product_id": product_id,
    }


def not_found(payload: Dict[str, Any]):
    """Handler for when no route is matched."""
    logging.warning(f"No route found for request with payload: {payload}")
    return {"error": "Not Found"}, 404


# --- Router ---
# A simple router class to map (method, url_pattern) to handler functions.


class Router:
    """
    Handles routing of webhook requests to the appropriate handler.
    """

    def __init__(self):
        # List to store tuples of (HTTP_METHOD, compiled_regex, handler_function)
        self.routes: List[Tuple[str, re.Pattern, Callable]] = []
        # Regex for capturing UUIDs in paths
        self.uuid_pattern = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"

    def add_route(self, method: str, path_template: str, handler: Callable):
        """
        Registers a new route.
        - method: HTTP method (e.g., "POST", "DELETE").
        - path_template: A path string with placeholders like {uuid}.
        - handler: The function to call on a match.
        """
        path_regex = path_template.replace("{uuid}", f"({self.uuid_pattern})")
        self.routes.append((method.upper(), re.compile(f"^{path_regex}$"), handler))
        logging.info(f"Registered route: {method.upper()} {path_template}")

    async def do_route(self, request: Request):
        """
        Processes an incoming request, finds a matching route, and calls its handler.
        """
        try:
            webhook_payload = await request.json()
        except json.JSONDecodeError:
            logging.error("Failed to parse request body as JSON")
            return {"error": "Invalid JSON payload"}, 400

        method = webhook_payload.get("method")
        url = webhook_payload.get("url")

        if not method or not url:
            logging.warning("Webhook payload missing 'method' or 'url'")
            return {
                "error": "Invalid webhook payload, 'method' and 'url' are required."
            }, 400

        logging.info(f"Routing request: {method} {url}")

        for route_method, route_pattern, handler in self.routes:
            if method == route_method:
                match = route_pattern.match(url)
                if match:
                    args = match.groups()
                    logging.info(
                        f"Matched route: {handler.__name__} with args: {args} and payload: {webhook_payload}"
                    )
                    response = handler(*args, payload=webhook_payload)
                    return response

        return not_found(webhook_payload)


# --- FastAPI App and Route Registration ---

app = FastAPI(title="Provisioner Webhook Handler")

# Global router instance
router = Router()

# Register all routes here to make them easy to find.
# This makes the application more extensible.
logging.info("Registering routes...")
router.add_route("POST", "/api/v2/data_products", handle_create_data_product)
router.add_route("PUT", "/api/v2/data_products/{uuid}", handle_update_data_product)
router.add_route(
    "POST",
    "/api/v2/data_products/{uuid}/output_ports/{uuid}/input_ports/approve",
    handle_approve_link,
)
router.add_route("DELETE", "/api/v2/data_products/{uuid}", handle_delete_data_product)
logging.info("Route registration complete.")


@app.get("/")
def get_root(request: Request):
    """Basic root endpoint for health checks."""
    logging.debug(
        f"GET request from {request.client.host if request.client else 'unknown'}"
    )
    return {"status": "ok"}


@app.post("/")
async def post_root(request: Request):
    """
    Main webhook entrypoint. It delegates request handling to the router.
    """
    logging.info(
        f"Received POST request from {request.client.host if request.client else 'unknown'}"
    )
    return await router.do_route(request)


# The PUT and DELETE endpoints are kept for now, but the primary logic
# for the webhook is handled by POST /.


@app.put("/")
def put_root(request: Request):
    logging.debug(
        f"PUT request from {request.client.host if request.client else 'unknown'}"
    )
    return {
        "status": "ok",
        "message": "This endpoint is not actively used for webhook routing.",
    }


@app.delete("/")
def delete_root(request: Request):
    logging.debug(
        f"DELETE request from {request.client.host if request.client else 'unknown'}"
    )
    return {
        "status": "ok",
        "message": "This endpoint is not actively used for webhook routing.",
    }
