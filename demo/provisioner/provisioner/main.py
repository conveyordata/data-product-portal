import logging
import re
import os
import requests
from cookiecutter.main import cookiecutter
from fastapi import FastAPI, Request
from typing import Callable, List, Tuple, Dict, Any
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Route Handlers ---
# These are example functions that will be called when a route matches.
# They can be moved to different files as the application grows.


def handle_create_data_product(payload: Dict[str, Any]):
    """Handler for creating a data product."""
    logging.info(f"Creating data product with payload: {payload}")
    # Example: extract data from payload and create a resource
    # The response from the original webhook is in payload['response']

    # use the payload to get more information regarding the product
    response_data = json.loads(payload.get("response", "{}"))
    data_product_id = response_data.get("id")

    if not data_product_id:
        logging.error("Could not find data product id in response")
        return {
            "status": "error",
            "message": "Could not find data product id in response",
        }

    # get the namespace of the data product
    portal_url = os.environ.get("DATA_PRODUCT_PORTAL_URL", "http://localhost:8080")

    try:
        response = requests.get(f"{portal_url}/api/data_products/{data_product_id}")
        response.raise_for_status()
        data_product_details = response.json()
        namespace = data_product_details.get("namespace")
        logging.info(f"Data product namespace: {namespace}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get data product details: {e}")
        return {
            "status": "error",
            "message": f"Failed to get data product details for id {data_product_id}",
        }

    # call the cookiecutter template
    context = {"project_name": namespace}
    cookiecutter(
        "/Users/pascalknapen/Code/dataminded/data-product-portal/demo/provisioner/templates/dbt",
        no_input=True,
        extra_context=context,
        output_dir="/Users/pascalknapen/Code/dataminded/data-product-portal/demo/products",
    )

    return {
        "status": "success",
        "action": "create_data_product",
        "original_response": json.loads(payload.get("response", "{}")),
    }


def handle_approve_link(link_id: str, payload: Dict[str, Any]):
    """Handler for approving a data product link."""
    logging.info(f"Approving link {link_id} with payload: {payload}")
    return {"status": "success", "action": "approve_link", "link_id": link_id}


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
                    logging.info(f"Matched route: {handler.__name__} with args: {args}")
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
router.add_route("POST", "/api/data_products", handle_create_data_product)
router.add_route(
    "POST", "/api/data_product_dataset_links/approve/{uuid}", handle_approve_link
)
router.add_route("DELETE", "/api/data_products/{uuid}", handle_delete_data_product)
logging.info("Route registration complete.")


@app.get("/")
def get_root(request: Request):
    """Basic root endpoint for health checks."""
    logging.debug(f"GET request from {request.client.host}")
    return {"status": "ok"}


@app.post("/")
async def post_root(request: Request):
    """
    Main webhook entrypoint. It delegates request handling to the router.
    """
    logging.info(f"Received POST request from {request.client.host}")
    return await router.do_route(request)


# The PUT and DELETE endpoints are kept for now, but the primary logic
# for the webhook is handled by POST /.


@app.put("/")
def put_root(request: Request):
    logging.debug(f"PUT request from {request.client.host}")
    return {
        "status": "ok",
        "message": "This endpoint is not actively used for webhook routing.",
    }


@app.delete("/")
def delete_root(request: Request):
    logging.debug(f"DELETE request from {request.client.host}")
    return {
        "status": "ok",
        "message": "This endpoint is not actively used for webhook routing.",
    }
