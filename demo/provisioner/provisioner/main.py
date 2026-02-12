import logging
import re
import os
import requests
import secrets
import string
from cookiecutter.main import cookiecutter
from fastapi import FastAPI, Request
from typing import Callable, List, Tuple, Dict, Any
import json
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# get the namespace of the data product
portal_url = os.environ.get("PROV_DPP_API_URL", "http://localhost:")
template_path = os.environ.get(
    "PROV_TEMPLATE_PATH",
    "/templates/sqlmesh",
)
tempplate_output_path = os.environ.get(
    "PROV_TEMPLATE_OUTPUT_PATH",
    "/products",
)

# S3 Configuration
s3_endpoint = os.environ.get("S3_ENDPOINT", "http://rustfs:9000")
s3_access_key = os.environ.get("S3_ACCESS_KEY", "minioadmin")
s3_secret_key = os.environ.get("S3_SECRET_KEY", "minioadmin")
s3_bucket_name = "data-products"

# In-memory cache for data product lifecycles
lifecycle_cache: Dict[str, Any] = {}

# In-memory cache for platform service configurations
platform_service_configurations_cache: Dict[str, Any] = {}

# In-memory store for project credentials (in production, use a real secrets manager)
credentials_store: Dict[str, Dict[str, str]] = {}


# --- Route Handlers ---
# These are example functions that will be called when a route matches.
# They can be moved to different files as the application grows.


def get_lifecycles() -> List[Dict[str, Any]]:
    """
    Fetches data product lifecycles from the API, with in-memory caching.
    """
    global lifecycle_cache
    if "lifecycles" in lifecycle_cache:
        logging.info("Returning cached lifecycles")
        return lifecycle_cache["lifecycles"]

    try:
        url = f"{portal_url}/api/v2/configuration/data_product_lifecycles"
        logging.info(f"Fetching lifecycles from {url}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        lifecycles = data.get("data_product_life_cycles", [])
        lifecycle_cache["lifecycles"] = lifecycles
        logging.info(f"Successfully fetched and cached {len(lifecycles)} lifecycles")
        return lifecycles
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get lifecycles: {e}")
        return []
    except json.JSONDecodeError:
        logging.error("Failed to parse lifecycles JSON response")
        return []


def get_platform_service_configurations() -> List[Dict[str, Any]]:
    """
    Fetches platform service configurations from the API, with in-memory caching.
    """
    global platform_service_configurations_cache
    if "platform_service_configurations" in platform_service_configurations_cache:
        logging.info("Returning cached platform service configurations")
        return platform_service_configurations_cache["platform_service_configurations"]

    try:
        url = f"{portal_url}/api/v2/configuration/platforms/configs"
        logging.info(f"Fetching platform service configurations from {url}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        configs = data.get("platform_service_configurations", [])
        platform_service_configurations_cache["platform_service_configurations"] = (
            configs
        )
        logging.info(
            f"Successfully fetched and cached {len(configs)} platform service configurations"
        )
        return configs
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get platform service configurations: {e}")
        return []
    except json.JSONDecodeError:
        logging.error("Failed to parse platform service configurations JSON response")
        return []


# --- S3 Helper Functions ---


def get_s3_client():
    """
    Creates and returns a boto3 S3 client configured for rustfs.
    """
    return boto3.client(
        "s3",
        endpoint_url=s3_endpoint,
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",  # rustfs doesn't care about region but boto3 requires it
    )


def ensure_bucket_exists(bucket_name: str):
    """
    Ensures that the S3 bucket exists, creates it if it doesn't.
    """
    s3_client = get_s3_client()
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        logging.info(f"Bucket '{bucket_name}' already exists")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            logging.info(f"Creating bucket '{bucket_name}'")
            try:
                s3_client.create_bucket(Bucket=bucket_name)
                logging.info(f"Successfully created bucket '{bucket_name}'")
            except ClientError as create_error:
                logging.error(f"Failed to create bucket: {create_error}")
                raise
        else:
            logging.error(f"Error checking bucket: {e}")
            raise


def create_s3_prefix(bucket_name: str, prefix: str):
    """
    Creates a prefix (folder) in S3 bucket.
    S3 doesn't have folders, but we can create a marker object.
    """
    s3_client = get_s3_client()
    try:
        # Create a marker object to represent the "folder"
        key = f"{prefix}/.keep" if not prefix.endswith("/") else f"{prefix}.keep"
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=b"")
        logging.info(f"Created S3 prefix: s3://{bucket_name}/{prefix}")
    except ClientError as e:
        logging.error(f"Failed to create S3 prefix: {e}")
        raise


def generate_aws_credentials() -> Tuple[str, str]:
    """
    Generates AWS-style credentials.
    Access Key: 20 characters (uppercase + digits)
    Secret Key: 40 characters (alphanumeric + special chars)
    """
    # AWS access keys start with 'AKIA' for IAM users, but for simplicity we'll use random
    access_key_chars = string.ascii_uppercase + string.digits
    access_key = "AKIA" + "".join(secrets.choice(access_key_chars) for _ in range(16))

    # AWS secret keys are base64-like (40 chars)
    secret_key_chars = string.ascii_letters + string.digits + "+/"
    secret_key = "".join(secrets.choice(secret_key_chars) for _ in range(40))

    return access_key, secret_key


def write_env_file(project_path: str, namespace: str, access_key: str, secret_key: str):
    """
    Writes the .env file with S3 credentials to the project directory.
    """
    env_content = f"""# S3 Configuration
# Generated by Data Product Portal Provisioner
# DO NOT COMMIT THIS FILE

S3_ENDPOINT={s3_endpoint}
S3_BUCKET={s3_bucket_name}
S3_PREFIX={namespace}
S3_ACCESS_KEY={access_key}
S3_SECRET_KEY={secret_key}
"""

    env_file_path = os.path.join(project_path, ".env")
    try:
        with open(env_file_path, "w") as f:
            f.write(env_content)
        logging.info(f"Wrote .env file to {env_file_path}")
    except IOError as e:
        logging.error(f"Failed to write .env file: {e}")
        raise


def handle_create_data_product(payload: Dict[str, Any]):
    """Handler for creating a data product."""
    logging.info(f"Creating data product with payload: {payload}")

    # Extract data product ID from webhook payload
    response_data = json.loads(payload.get("response", "{}"))
    data_product_id = response_data.get("id")

    if not data_product_id:
        logging.error("Could not find data product id in response")
        return {
            "status": "error",
            "message": "Could not find data product id in response",
        }

    # Fetch data product details from portal
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

    # Step 1: Ensure S3 bucket exists and create prefix
    try:
        ensure_bucket_exists(s3_bucket_name)
        create_s3_prefix(s3_bucket_name, namespace)
    except Exception as e:
        logging.error(f"Failed to set up S3 storage: {e}")
        return {
            "status": "error",
            "message": f"Failed to set up S3 storage: {str(e)}",
        }

    # Step 2: Generate credentials
    access_key, secret_key = generate_aws_credentials()

    # Store credentials in memory (for future regeneration on link approval)
    credentials_store[namespace] = {"access_key": access_key, "secret_key": secret_key}
    logging.info(f"Generated credentials for namespace: {namespace}")

    # Step 3: Scaffold SQLMesh project using cookiecutter
    try:
        context = {
            "project_name": namespace,
            "s3_endpoint": s3_endpoint,
            "s3_bucket": s3_bucket_name,
            "s3_prefix": namespace,
            "s3_access_key": access_key,
            "s3_secret_key": secret_key,
        }

        cookiecutter(
            template_path,
            no_input=True,
            extra_context=context,
            output_dir=tempplate_output_path,
        )

        project_path = os.path.join(tempplate_output_path, namespace)
        logging.info(f"Successfully scaffolded project at: {project_path}")

        # Step 4: Write .env file with S3 credentials
        write_env_file(project_path, namespace, access_key, secret_key)

    except Exception as e:
        logging.error(f"Failed to scaffold project: {e}")
        return {
            "status": "error",
            "message": f"Failed to scaffold project: {str(e)}",
        }

    # Update the data product lifecycle to "Ready" state (keeping existing logic)
    lifecycles = get_lifecycles()
    ready_lifecycle = next((lc for lc in lifecycles if lc.get("name") == "Ready"), None)

    if ready_lifecycle:
        ready_lifecycle_id = ready_lifecycle.get("id")

        try:
            update_payload = {
                "name": data_product_details.get("name"),
                "namespace": data_product_details.get("namespace"),
                "description": data_product_details.get("description"),
                "type_id": data_product_details.get("type", {}).get("id"),
                "lifecycle_id": ready_lifecycle_id,
                "domain_id": data_product_details.get("domain", {}).get("id"),
                "tag_ids": [tag["id"] for tag in data_product_details.get("tags", [])],
            }

            update_url = f"{portal_url}/api/data_products/{data_product_id}"
            logging.info(f"Updating data product to 'Ready' state at {update_url}")

            update_response = requests.put(update_url, json=update_payload)
            update_response.raise_for_status()

            logging.info(
                f"Successfully updated data product {data_product_id} to 'Ready' state."
            )
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to update data product state: {e}")
            if e.response is not None:
                logging.error(f"Response body: {e.response.text}")

    # Optionally create PostgreSQL output port (keeping existing logic)
    configs = get_platform_service_configurations()
    postgres_config = next(
        (c for c in configs if c.get("service", {}).get("name") == "PostgreSQL"), None
    )

    if postgres_config:
        platform_id = postgres_config.get("platform", {}).get("id")
        service_id = postgres_config.get("service", {}).get("id")
        schema_name = data_product_details.get("namespace", "").replace("-", "_")

        output_port_payload = {
            "name": data_product_details.get("name"),
            "namespace": data_product_details.get("namespace"),
            "description": data_product_details.get("description"),
            "tag_ids": [],
            "status": "active",
            "sourceAligned": True,
            "platform_id": platform_id,
            "service_id": service_id,
            "configuration": {
                "configuration_type": "PostgreSQLDataOutput",
                "database": "dpp_demo",
                "schema": schema_name,
                "entire_schema": True,
            },
            "result": f"dpp_demo.{schema_name}.*",
        }

        try:
            output_port_url = (
                f"{portal_url}/api/data_products/{data_product_id}/data_output"
            )
            logging.info(f"Creating data output port at {output_port_url}")

            output_port_response = requests.post(
                output_port_url, json=output_port_payload
            )
            output_port_response.raise_for_status()
            logging.info(
                f"Successfully created data output port for data product {data_product_id}."
            )
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to create data output port: {e}")
            if e.response is not None:
                logging.error(f"Response body: {e.response.text}")

    return {
        "status": "success",
        "action": "create_data_product",
        "namespace": namespace,
        "s3_location": f"s3://{s3_bucket_name}/{namespace}",
        "project_path": f"/products/{namespace}",
    }


def handle_approve_link(link_id: str, payload: Dict[str, Any]):
    """
    Handler for approving a data product link.
    When a link is approved, regenerate credentials for the consumer.
    """
    logging.info(f"Approving link {link_id} with payload: {payload}")

    # Extract link details from payload (the response may contain link info)
    # For this POC, we'll try to get the consumer data product info
    try:
        # The webhook payload should contain information about the link
        # We need to identify the consumer data product and regenerate its credentials

        # Parse the original response to get link details
        response_data = json.loads(payload.get("response", "{}"))
        logging.info(f"Link approval response data: {response_data}")

        # In a real scenario, you'd fetch the link details from the API
        # For now, we'll extract from the payload if available
        # The consumer is the data product that's consuming the data

        # Example: fetch link details (this would typically come from the API)
        # For POC purposes, we'll assume the link info is in the payload
        # You might need to adjust this based on actual webhook structure

        consumer_namespace = payload.get("consumer_namespace")

        if not consumer_namespace:
            logging.warning(
                "Consumer namespace not found in payload, skipping credential regeneration"
            )
            return {
                "status": "success",
                "action": "approve_link",
                "link_id": link_id,
                "message": "Link approved, but consumer namespace not provided",
            }

        # Regenerate credentials for the consumer
        access_key, secret_key = generate_aws_credentials()

        # Update credentials store
        credentials_store[consumer_namespace] = {
            "access_key": access_key,
            "secret_key": secret_key,
        }

        # Update the consumer's .env file
        consumer_project_path = os.path.join(tempplate_output_path, consumer_namespace)

        if os.path.exists(consumer_project_path):
            write_env_file(
                consumer_project_path, consumer_namespace, access_key, secret_key
            )
            logging.info(f"Regenerated credentials for consumer: {consumer_namespace}")

            return {
                "status": "success",
                "action": "approve_link",
                "link_id": link_id,
                "consumer_namespace": consumer_namespace,
                "message": "Link approved and consumer credentials regenerated",
            }
        else:
            logging.warning(f"Consumer project path not found: {consumer_project_path}")
            return {
                "status": "partial_success",
                "action": "approve_link",
                "link_id": link_id,
                "message": f"Link approved but consumer project not found at {consumer_project_path}",
            }

    except Exception as e:
        logging.error(f"Error handling link approval: {e}")
        return {
            "status": "error",
            "action": "approve_link",
            "link_id": link_id,
            "message": f"Error: {str(e)}",
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
