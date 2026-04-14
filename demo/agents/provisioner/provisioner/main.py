import logging
import re
import os
import threading
import requests
import psycopg2
import yaml
from fastapi import FastAPI, Request
from typing import Callable, List, Tuple, Dict, Any
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

portal_url = os.environ.get("PROV_DPP_API_URL", "http://localhost:8080")
output_path = os.environ.get("PROV_TEMPLATE_OUTPUT_PATH", "/products")
agent_configs_path = os.environ.get("PROV_AGENT_CONFIGS_PATH", "/agent_configs")

demo_db_host = os.environ.get("PROV_DEMO_DB_HOST", "postgresql-demo")
demo_db_port = int(os.environ.get("PROV_DEMO_DB_PORT", "5432"))
demo_db_name = os.environ.get("PROV_DEMO_DB_NAME", "dpp_demo")
demo_db_admin_user = os.environ.get("PROV_DEMO_DB_ADMIN_USER", "postgres")
demo_db_admin_password = os.environ.get("PROV_DEMO_DB_ADMIN_PASSWORD", "abc123")

# Per-namespace locks to prevent concurrent YAML read-modify-write races
_yaml_locks: Dict[str, threading.Lock] = {}
_yaml_locks_mutex = threading.Lock()


def get_yaml_lock(namespace: str) -> threading.Lock:
    with _yaml_locks_mutex:
        if namespace not in _yaml_locks:
            _yaml_locks[namespace] = threading.Lock()
        return _yaml_locks[namespace]


# In-memory cache for data product lifecycles
lifecycle_cache: Dict[str, Any] = {}

# In-memory cache for platform service configurations
platform_service_configurations_cache: Dict[str, Any] = {}


def get_db_connection():
    return psycopg2.connect(
        host=demo_db_host,
        port=demo_db_port,
        dbname=demo_db_name,
        user=demo_db_admin_user,
        password=demo_db_admin_password,
    )


def get_lifecycles() -> List[Dict[str, Any]]:
    global lifecycle_cache
    if "lifecycles" in lifecycle_cache:
        return lifecycle_cache["lifecycles"]

    try:
        url = f"{portal_url}/api/v2/configuration/data_product_lifecycles"
        response = requests.get(url)
        response.raise_for_status()
        lifecycles = response.json().get("data_product_life_cycles", [])
        lifecycle_cache["lifecycles"] = lifecycles
        return lifecycles
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        logging.error(f"Failed to get lifecycles: {e}")
        return []


def get_platform_service_configurations() -> List[Dict[str, Any]]:
    global platform_service_configurations_cache
    if "platform_service_configurations" in platform_service_configurations_cache:
        return platform_service_configurations_cache["platform_service_configurations"]

    try:
        url = f"{portal_url}/api/v2/configuration/platforms/configs"
        response = requests.get(url)
        response.raise_for_status()
        configs = response.json().get("platform_service_configurations", [])
        platform_service_configurations_cache["platform_service_configurations"] = (
            configs
        )
        return configs
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        logging.error(f"Failed to get platform service configurations: {e}")
        return []


def provision_db_schema(schema_name: str, db_user: str, db_password: str):
    """Create schema user and grant permissions in the demo database."""
    conn = get_db_connection()
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (db_user,))
            if not cur.fetchone():
                cur.execute(f"CREATE USER {db_user} WITH PASSWORD %s", (db_password,))
            cur.execute(f"GRANT USAGE ON SCHEMA {schema_name} TO {db_user}")
            cur.execute(
                f"GRANT SELECT ON ALL TABLES IN SCHEMA {schema_name} TO {db_user}"
            )
        logging.info(f"Provisioned schema {schema_name} with user {db_user}")
    finally:
        conn.close()


def create_technical_asset(
    data_product_id: str,
    data_product_details: Dict[str, Any],
    platform_id: str,
    service_id: str,
    configuration: Dict[str, Any],
    result: str,
    namespace: str | None = None,
) -> str:
    """Create a technical asset and activate it. Returns the asset ID."""
    payload: Dict[str, Any] = {
        "name": data_product_details.get("name"),
        "namespace": namespace or data_product_details.get("namespace"),
        "description": data_product_details.get("description"),
        "tag_ids": [],
        "status": "active",
        "technical_mapping": "custom",
        "platform_id": platform_id,
        "service_id": service_id,
        "configuration": configuration,
        "result": result,
    }

    url = f"{portal_url}/api/v2/data_products/{data_product_id}/technical_assets"
    response = requests.post(url, json=payload)
    response.raise_for_status()
    asset_id = response.json().get("id")
    logging.info(f"Created technical asset {asset_id}")

    # Activate
    status_url = f"{portal_url}/api/v2/data_products/{data_product_id}/technical_assets/{asset_id}/status"
    status_response = requests.put(status_url, json={"status": "active"})
    status_response.raise_for_status()
    logging.info(f"Activated technical asset {asset_id}")

    return asset_id


def write_agent_config(
    namespace: str,
    name: str,
    description: str,
    about: str,
    schema_name: str,
    db_user: str,
    db_password: str,
):
    """Write the agent config YAML for the Agno agent server."""
    # Strip HTML from about text for instructions
    import re as _re

    instructions = _re.sub(r"<[^>]+>", " ", about or "").strip()
    instructions = _re.sub(r"\s+", " ", instructions)

    config = {
        "name": f"{name} Agent",
        "description": description,
        "instructions": instructions,
        "osi_files": [f"/products/{namespace}/osi.yml"],
        "allowed_schemas": [schema_name],
        "postgres": {
            "host": demo_db_host,
            "port": demo_db_port,
            "database": demo_db_name,
            "user": db_user,
            "password": db_password,
        },
    }

    os.makedirs(agent_configs_path, exist_ok=True)
    config_path = os.path.join(agent_configs_path, f"{namespace}.yml")
    with get_yaml_lock(namespace):
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    logging.info(f"Wrote agent config to {config_path}")


def handle_create_data_product(payload: Dict[str, Any]):
    """Handler for creating a data product."""
    logging.info("Creating data product")
    try:
        response_data = json.loads(payload.get("response") or "{}")
    except (json.JSONDecodeError, TypeError):
        response_data = {}
    if not isinstance(response_data, dict):
        response_data = {}
    data_product_id = response_data.get("id")

    if not data_product_id:
        logging.error("Could not find data product id in response")
        return {
            "status": "error",
            "message": "Could not find data product id in response",
        }

    try:
        response = requests.get(f"{portal_url}/api/v2/data_products/{data_product_id}")
        response.raise_for_status()
        dp = response.json()
        namespace = dp.get("namespace")
        name = dp.get("name")
        description = dp.get("description", "")
        about = dp.get("about", "")
        logging.info(f"Data product namespace: {namespace}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get data product details: {e}")
        return {
            "status": "error",
            "message": f"Failed to get data product details for id {data_product_id}",
        }

    schema_name = namespace.replace("-", "_")
    db_user = f"{schema_name}_user"
    db_password = f"{schema_name}_pwd"

    # Provision DB schema and user
    try:
        provision_db_schema(schema_name, db_user, db_password)
    except Exception as e:
        logging.error(f"Failed to provision DB schema: {e}")
        return {"status": "error", "message": f"Failed to provision DB schema: {e}"}

    configs = get_platform_service_configurations()

    # Create OSI technical asset
    osi_config = next(
        (c for c in configs if c.get("service", {}).get("name") == "OSI"), None
    )
    if osi_config:
        try:
            create_technical_asset(
                data_product_id=data_product_id,
                data_product_details=dp,
                platform_id=osi_config.get("platform", {}).get("id"),
                service_id=osi_config.get("service", {}).get("id"),
                configuration={
                    "configuration_type": "OSISemanticModelTechnicalAssetConfiguration",
                    "model_name": f"{name} Semantic Model",
                    "file_path": f"/products/{namespace}/osi.yml",
                },
                result=f"{name} Semantic Model",
                namespace=f"{namespace}-semantic",
            )
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to create OSI technical asset: {e}")
            if e.response is not None:
                logging.error(f"Response body: {e.response.text}")
    else:
        logging.warning("OSI service configuration not found, skipping OSI asset")

    # Create PostgreSQL technical asset
    postgres_config = next(
        (c for c in configs if c.get("service", {}).get("name") == "PostgreSQL"), None
    )
    if not postgres_config:
        logging.error("Could not find 'PostgreSQL' service configuration.")
        return {
            "status": "error",
            "message": "Configuration error: 'PostgreSQL' service not found.",
        }

    try:
        create_technical_asset(
            data_product_id=data_product_id,
            data_product_details=dp,
            platform_id=postgres_config.get("platform", {}).get("id"),
            service_id=postgres_config.get("service", {}).get("id"),
            configuration={
                "configuration_type": "PostgreSQLTechnicalAssetConfiguration",
                "database": demo_db_name,
                "schema": schema_name,
                "access_granularity": "schema",
                "table": "*",
            },
            result=f"{demo_db_name}.{schema_name}.*",
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to create PostgreSQL technical asset: {e}")
        if e.response is not None:
            logging.error(f"Response body: {e.response.text}")
        return {
            "status": "error",
            "message": f"Failed to create PostgreSQL technical asset for id {data_product_id}",
        }

    # Write agent config
    write_agent_config(
        namespace=namespace,
        name=name,
        description=description,
        about=about,
        schema_name=schema_name,
        db_user=db_user,
        db_password=db_password,
    )

    # Update lifecycle to "Ready"
    lifecycles = get_lifecycles()
    ready_lifecycle = next((lc for lc in lifecycles if lc.get("name") == "Ready"), None)
    if not ready_lifecycle:
        logging.error("Could not find 'Ready' lifecycle state.")
        return {
            "status": "error",
            "message": "Configuration error: 'Ready' lifecycle not found.",
        }

    try:
        update_payload = {
            "name": dp.get("name"),
            "namespace": dp.get("namespace"),
            "description": dp.get("description"),
            "type_id": dp.get("type", {}).get("id"),
            "lifecycle_id": ready_lifecycle.get("id"),
            "domain_id": dp.get("domain", {}).get("id"),
            "tag_ids": [tag["id"] for tag in dp.get("tags", [])],
        }
        update_response = requests.put(
            f"{portal_url}/api/v2/data_products/{data_product_id}", json=update_payload
        )
        update_response.raise_for_status()
        logging.info(f"Updated data product {data_product_id} to 'Ready' state.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to update data product state: {e}")
        if e.response is not None:
            logging.error(f"Response body: {e.response.text}")
        return {
            "status": "error",
            "message": f"Failed to update data product state for id {data_product_id}",
        }

    return {
        "status": "success",
        "action": "create_data_product",
        "original_response": json.loads(payload.get("response", "{}")),
    }


def handle_approve_link(
    provider_dp_id: str, output_port_id: str, payload: Dict[str, Any]
):
    """Handler for approving a data product input port link."""
    logging.info(
        f"Approving link: provider_dp_id={provider_dp_id}, output_port_id={output_port_id}"
    )

    # The approve endpoint returns None, so response is empty — look up approved
    # input ports directly from the portal instead.
    consumer_data_product_id = None
    try:
        ip_response = requests.get(
            f"{portal_url}/api/v2/data_products/{provider_dp_id}"
            f"/output_ports/{output_port_id}/input_ports"
        )
        ip_response.raise_for_status()
        input_ports = ip_response.json().get("input_ports", [])
        # Pick the most recently approved link
        approved = [ip for ip in input_ports if ip.get("status") == "approved"]
        if approved:
            # Sort by requested_on descending and take the latest
            approved.sort(key=lambda x: x.get("requested_on", ""), reverse=True)
            consumer_data_product_id = approved[0].get("data_product_id")
    except requests.exceptions.RequestException as e:
        logging.error(
            f"Failed to fetch input ports for output port {output_port_id}: {e}"
        )

    if not consumer_data_product_id:
        logging.warning(
            "Could not determine consumer_data_product_id; skipping DB grant"
        )
        return {
            "status": "success",
            "action": "approve_link",
            "note": "no approved consumer found",
        }

    # Get provider and consumer namespaces
    try:
        provider_response = requests.get(
            f"{portal_url}/api/v2/data_products/{provider_dp_id}"
        )
        provider_response.raise_for_status()
        provider_namespace = provider_response.json().get("namespace")

        consumer_response = requests.get(
            f"{portal_url}/api/v2/data_products/{consumer_data_product_id}"
        )
        consumer_response.raise_for_status()
        consumer_namespace = consumer_response.json().get("namespace")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data product details: {e}")
        return {"status": "error", "message": "Failed to fetch data product details"}

    provider_schema = provider_namespace.replace("-", "_")
    consumer_schema = consumer_namespace.replace("-", "_")
    consumer_user = f"{consumer_schema}_user"

    # Grant consumer user access to provider schema
    try:
        conn = get_db_connection()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"GRANT USAGE ON SCHEMA {provider_schema} TO {consumer_user}")
            cur.execute(
                f"GRANT SELECT ON ALL TABLES IN SCHEMA {provider_schema} TO {consumer_user}"
            )
        conn.close()
        logging.info(f"Granted {consumer_user} access to schema {provider_schema}")
    except Exception as e:
        logging.error(f"Failed to grant DB access: {e}")
        return {"status": "error", "message": f"Failed to grant DB access: {e}"}

    # Update consumer agent config to include provider OSI file
    config_path = os.path.join(agent_configs_path, f"{consumer_namespace}.yml")
    if os.path.exists(config_path):
        with get_yaml_lock(consumer_namespace):
            with open(config_path) as f:
                config = yaml.safe_load(f)

            provider_osi = f"/products/{provider_namespace}/osi.yml"
            osi_files = config.get("osi_files", [])
            if provider_osi not in osi_files:
                osi_files.append(provider_osi)
                config["osi_files"] = osi_files

            schemas = config.get("allowed_schemas", [])
            if provider_schema not in schemas:
                schemas.append(provider_schema)
                config["allowed_schemas"] = schemas

            with open(config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            logging.info(
                f"Updated agent config for {consumer_namespace} with {provider_osi}"
            )
    else:
        logging.warning(
            f"Agent config not found for consumer {consumer_namespace}: {config_path}"
        )

    return {
        "status": "success",
        "action": "approve_link",
        "provider": provider_namespace,
        "consumer": consumer_namespace,
    }


def handle_link_input_ports(consumer_dp_id: str, payload: Dict[str, Any]):
    """Handler for POST /api/v2/data_products/{uuid}/link_input_ports.

    Fires when a consumer data product links to output ports. Publicly-accessible
    ports are auto-approved immediately, so we iterate the returned link IDs and
    grant DB access + update the consumer agent YAML for every approved link.
    """
    logging.info(f"Handling link_input_ports for consumer {consumer_dp_id}")

    # Parse the link association IDs from the webhook response
    try:
        response_data = json.loads(payload.get("response") or "{}")
    except (json.JSONDecodeError, TypeError):
        response_data = {}
    if not isinstance(response_data, dict):
        response_data = {}
    new_link_ids = set(response_data.get("input_port_links", []))

    if not new_link_ids:
        logging.info("No input_port_links in response, nothing to do")
        return {"status": "success", "action": "link_input_ports", "note": "no links"}

    # Get consumer namespace
    try:
        consumer_resp = requests.get(
            f"{portal_url}/api/v2/data_products/{consumer_dp_id}"
        )
        consumer_resp.raise_for_status()
        consumer_namespace = consumer_resp.json().get("namespace")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch consumer data product {consumer_dp_id}: {e}")
        return {"status": "error", "message": str(e)}

    consumer_schema = consumer_namespace.replace("-", "_")
    consumer_user = f"{consumer_schema}_user"

    # Get all input port associations for this consumer
    try:
        ip_resp = requests.get(
            f"{portal_url}/api/v2/data_products/{consumer_dp_id}/input_ports"
        )
        ip_resp.raise_for_status()
        all_input_ports = ip_resp.json().get("input_ports", [])
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch input ports for {consumer_dp_id}: {e}")
        return {"status": "error", "message": str(e)}

    # Filter to only the newly linked AND approved ports
    approved_links = [
        ip
        for ip in all_input_ports
        if str(ip.get("id")) in new_link_ids and ip.get("status") == "approved"
    ]

    if not approved_links:
        logging.info(
            f"None of the {len(new_link_ids)} new links are approved yet — "
            "likely pending manual approval"
        )
        return {
            "status": "success",
            "action": "link_input_ports",
            "note": "no approved links",
        }

    # Resolve provider namespaces and grant DB access (outside the lock)
    _cp = os.path.join(agent_configs_path, f"{consumer_namespace}.yml")
    config_path: str | None = _cp if os.path.exists(_cp) else None
    if config_path is None:
        logging.warning(
            f"Agent config not found for {consumer_namespace}; skipping YAML update"
        )

    granted_providers = []
    for link in approved_links:
        provider_dp_id = link.get("input_port", {}).get("data_product_id")
        if not provider_dp_id:
            logging.warning(
                f"Could not extract provider DP id from link {link.get('id')}"
            )
            continue

        # Get provider namespace
        try:
            provider_resp = requests.get(
                f"{portal_url}/api/v2/data_products/{provider_dp_id}"
            )
            provider_resp.raise_for_status()
            provider_namespace = provider_resp.json().get("namespace")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch provider DP {provider_dp_id}: {e}")
            continue

        provider_schema = provider_namespace.replace("-", "_")

        # Grant consumer user access to provider schema
        try:
            conn = get_db_connection()
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(
                    f"GRANT USAGE ON SCHEMA {provider_schema} TO {consumer_user}"
                )
                cur.execute(
                    f"GRANT SELECT ON ALL TABLES IN SCHEMA {provider_schema}"
                    f" TO {consumer_user}"
                )
            conn.close()
            logging.info(f"Granted {consumer_user} access to schema {provider_schema}")
        except Exception as e:
            logging.error(f"Failed to grant DB access for {provider_schema}: {e}")
            continue

        granted_providers.append(provider_namespace)

    # Update agent YAML under lock so concurrent events don't clobber each other
    processed = []
    if config_path and granted_providers:
        with get_yaml_lock(consumer_namespace):
            with open(config_path) as f:
                config = yaml.safe_load(f) or {}

            osi_files = config.get("osi_files", [])
            schemas = config.get("allowed_schemas", [])
            for provider_namespace in granted_providers:
                provider_osi = f"/products/{provider_namespace}/osi.yml"
                if provider_osi not in osi_files:
                    osi_files.append(provider_osi)
                    processed.append(provider_namespace)
                provider_schema = provider_namespace.replace("-", "_")
                if provider_schema not in schemas:
                    schemas.append(provider_schema)

            if processed:
                config["osi_files"] = osi_files
                config["allowed_schemas"] = schemas
                with open(config_path, "w") as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                logging.info(
                    f"Updated agent config for {consumer_namespace}: added OSI files"
                    f" for {processed}"
                )

    return {
        "status": "success",
        "action": "link_input_ports",
        "consumer": consumer_namespace,
        "providers_granted": processed,
    }


def handle_update_data_product(product_id: str, payload: Dict[str, Any]):
    logging.info(f"Updating data product {product_id}")
    return {
        "status": "success",
        "action": "update_data_product",
        "product_id": product_id,
    }


def handle_update_about(product_id: str, payload: Dict[str, Any]):
    """Handler for updating a data product's about text — re-syncs agent YAML instructions."""
    logging.info(f"Updating about for data product {product_id}")

    try:
        response = requests.get(f"{portal_url}/api/v2/data_products/{product_id}")
        response.raise_for_status()
        dp = response.json()
        namespace = dp.get("namespace")
        about = dp.get("about", "")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get data product details: {e}")
        return {"status": "error", "message": str(e)}

    config_path = os.path.join(agent_configs_path, f"{namespace}.yml")
    if not os.path.exists(config_path):
        logging.info(f"No agent config found for {namespace}, skipping about sync")
        return {
            "status": "success",
            "action": "update_about",
            "note": "no agent config",
        }

    instructions = re.sub(r"<[^>]+>", " ", about or "").strip()
    instructions = re.sub(r"\s+", " ", instructions)

    with get_yaml_lock(namespace):
        with open(config_path) as f:
            config = yaml.safe_load(f)
        config["instructions"] = instructions
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    logging.info(f"Synced agent instructions from updated about for {namespace}")
    return {"status": "success", "action": "update_about", "namespace": namespace}


def handle_delete_data_product(product_id: str, payload: Dict[str, Any]):
    logging.info(f"Deleting data product {product_id}")
    return {
        "status": "success",
        "action": "delete_data_product",
        "product_id": product_id,
    }


def not_found(payload: Dict[str, Any]):
    logging.warning(f"No route found for request with payload: {payload}")
    return {"error": "Not Found"}, 404


class Router:
    def __init__(self):
        self.routes: List[Tuple[str, re.Pattern, Callable]] = []
        self.uuid_pattern = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"

    def add_route(self, method: str, path_template: str, handler: Callable):
        path_regex = path_template.replace("{uuid}", f"({self.uuid_pattern})")
        self.routes.append((method.upper(), re.compile(f"^{path_regex}$"), handler))
        logging.info(f"Registered route: {method.upper()} {path_template}")

    async def do_route(self, request: Request):
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


app = FastAPI(title="Provisioner Webhook Handler")
router = Router()

logging.info("Registering routes...")
router.add_route("POST", "/api/v2/data_products", handle_create_data_product)
router.add_route("PUT", "/api/v2/data_products/{uuid}", handle_update_data_product)
router.add_route("PUT", "/api/v2/data_products/{uuid}/about", handle_update_about)
router.add_route(
    "POST",
    "/api/v2/data_products/{uuid}/link_input_ports",
    handle_link_input_ports,
)
router.add_route(
    "POST",
    "/api/v2/data_products/{uuid}/output_ports/{uuid}/input_ports/approve",
    handle_approve_link,
)
router.add_route("DELETE", "/api/v2/data_products/{uuid}", handle_delete_data_product)
logging.info("Route registration complete.")


@app.get("/")
def get_root(request: Request):
    return {"status": "ok"}


@app.post("/")
async def post_root(request: Request):
    logging.info(f"Received POST request from {request.client.host}")
    return await router.do_route(request)


@app.put("/")
def put_root(request: Request):
    return {"status": "ok"}


@app.delete("/")
def delete_root(request: Request):
    return {"status": "ok"}
