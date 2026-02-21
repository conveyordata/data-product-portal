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
import subprocess
import tempfile
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
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
credentials_store: Dict[str, Dict[str, str | list[str]]] = {}


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


def run_mc_command(args: list, check=True) -> subprocess.CompletedProcess:
    """
    Run a MinIO mc command.

    Args:
        args: List of arguments for mc command
        check: Whether to raise exception on non-zero exit code

    Returns:
        CompletedProcess with stdout/stderr
    """
    cmd = ["mc"] + args
    logging.debug(f"Running mc command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if result.returncode != 0 and check:
        logging.error(f"mc command failed: {result.stderr}")
        raise RuntimeError(f"mc command failed: {result.stderr}")

    return result


def setup_mc_alias():
    """
    Configure mc alias for rustfs (MinIO) if not already configured.
    """
    # Check if alias exists
    result = run_mc_command(["alias", "list", "rustfs"], check=False)

    if "rustfs" not in result.stdout:
        # Configure the alias
        endpoint = s3_endpoint  # http://rustfs:9000
        logging.info(f"Configuring mc alias 'rustfs' -> {endpoint}")
        run_mc_command(
            [
                "alias",
                "set",
                "rustfs",
                endpoint,
                s3_access_key,  # minioadmin
                s3_secret_key,  # minioadmin
            ]
        )
        logging.info("✅ mc alias configured")
    else:
        logging.debug("mc alias 'rustfs' already configured")


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


def create_minio_user_with_policy(
    namespace: str, access_key: str, secret_key: str, allowed_prefixes: list
):
    """
    Create MinIO user and policy via mc admin commands.

    Args:
        namespace: Data product namespace
        access_key: MinIO access key
        secret_key: MinIO secret key
        allowed_prefixes: List of S3 prefixes this user can access
    """
    setup_mc_alias()

    policy_name = f"policy-{namespace}"

    # Build policy JSON for all allowed prefixes
    resources = []
    for prefix in allowed_prefixes:
        resources.append(f"arn:aws:s3:::{s3_bucket_name}/{prefix}/*")

    # Also need bucket-level permissions for ListBucket
    resources.append(f"arn:aws:s3:::{s3_bucket_name}")

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
                "Resource": resources[:-1],  # All prefix resources
            },
            {
                "Effect": "Allow",
                "Action": ["s3:ListAllMyBuckets"],
                "Resource": ["arn:aws:s3:::*"],
            },
            {
                "Effect": "Allow",
                "Action": ["s3:ListBucket"],
                "Resource": [resources[-1]],  # Bucket resource
                "Condition": {
                    "StringLike": {
                        "s3:prefix": [f"{prefix}/*" for prefix in allowed_prefixes]
                    }
                },
            },
        ],
    }

    # Write policy to temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(policy, f, indent=2)
        policy_file = f.name

    try:
        # Create or update policy
        logging.info(f"Creating MinIO policy: {policy_name}")
        result = run_mc_command(
            ["admin", "policy", "create", "rustfs", policy_name, policy_file],
            check=False,
        )

        if result.returncode != 0:
            # Policy might already exist, try to update it
            logging.info(f"Policy exists, updating: {policy_name}")
            # MinIO doesn't have a direct update - remove and recreate
            run_mc_command(
                ["admin", "policy", "remove", "rustfs", policy_name], check=False
            )
            run_mc_command(
                ["admin", "policy", "create", "rustfs", policy_name, policy_file]
            )

        # Check if user exists
        user_exists = run_mc_command(
            ["admin", "user", "info", "rustfs", access_key], check=False
        )

        if user_exists.returncode != 0:
            # Create user
            logging.info(f"Creating MinIO user: {access_key}")
            run_mc_command(["admin", "user", "add", "rustfs", access_key, secret_key])
        else:
            logging.info(f"User {access_key} already exists, updating password")
            # Update user password (remove and recreate)
            run_mc_command(
                ["admin", "user", "remove", "rustfs", access_key], check=False
            )
            run_mc_command(["admin", "user", "add", "rustfs", access_key, secret_key])

        # Attach policy to user
        logging.info(f"Attaching policy {policy_name} to user {access_key}")
        run_mc_command(
            ["admin", "policy", "attach", "rustfs", policy_name, "--user", access_key]
        )

        logging.info(f"✅ MinIO user {access_key} created with policy {policy_name}")
    finally:
        # Clean up temp file
        os.unlink(policy_file)


def generate_aws_credentials(namespace: str) -> Tuple[str, str]:
    """
    Creates a MinIO user with access limited to the data product's prefix.

    Args:
        namespace: The data product namespace (used as prefix)

    Returns:
        Tuple of (access_key, secret_key)
    """
    try:
        # Generate a unique access key ID based on namespace
        access_key = f"dp-{namespace}".replace("_", "-").replace(".", "-")[:20]

        # Generate a secure secret key
        secret_key = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(40)
        )

        logging.info(f"Generating credentials for {namespace}: access_key={access_key}")

        # Store credentials for later use
        credentials_store[namespace] = {
            "access_key": access_key,
            "secret_key": secret_key,
            "allowed_prefixes": [namespace],  # Initially only own prefix
        }

        # Create actual MinIO user with policy
        create_minio_user_with_policy(namespace, access_key, secret_key, [namespace])

        return access_key, secret_key

    except Exception as e:
        logging.error(
            f"Failed to create MinIO user for {namespace}: {e}", exc_info=True
        )
        # Fallback to shared credentials
        logging.warning("Falling back to shared minioadmin credentials")
        return s3_access_key, s3_secret_key


def write_env_file(project_path: str, namespace: str, access_key: str, secret_key: str):
    """
    Writes the .env file with S3 credentials to the project directory.
    """
    # Determine endpoint host based on environment
    # For Coder container, use 'rustfs', for localhost use 'localhost'
    env_content = f"""# S3 Configuration
# Generated by Data Product Portal Provisioner
# DO NOT COMMIT THIS FILE

# For local testing, use localhost. In Coder container, set to rustfs
S3_ENDPOINT_HOST=rustfs
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
        response = requests.get(f"{portal_url}/api/v2/data_products/{data_product_id}")
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
    access_key, secret_key = generate_aws_credentials(namespace)

    # Store credentials in memory (for future regeneration on link approval)
    # Note: credentials_store is already updated by generate_aws_credentials
    logging.info(f"Generated credentials for namespace: {namespace}")

    # Step 3: Scaffold SQLMesh project using cookiecutter
    try:
        context = {
            "project_name": namespace,
            "s3_endpoint": s3_endpoint,
            "s3_bucket": s3_bucket_name,
            "portal_url": portal_url,
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

        # Step 5: Make run.sh executable
        import stat

        run_sh_path = os.path.join(project_path, "run.sh")
        if os.path.exists(run_sh_path):
            os.chmod(run_sh_path, os.stat(run_sh_path).st_mode | stat.S_IEXEC)
            logging.info("Made run.sh executable")

    except Exception as e:
        logging.error(f"Failed to scaffold project: {e}")
        return {
            "status": "error",
            "message": f"Failed to scaffold project: {str(e)}",
        }

    if data_product_details.get("namespace") == "contact-survey-data":
        # Copy git project over into scaffolded project

        # Auto-create the output port and output tables
        try:
            # This is a bit of a hack - we want to auto-create the output port and tables for the contact-survey-data since it's used in the consumer demo, but we don't want to do this for every data product created from the template
            logging.info("Auto-creating output port and tables for contact-survey-data")
            # Fetch assigned roles for dp to get owners

            roles = (
                requests.get(
                    f"{portal_url}/api/v2/authz/role_assignments/data_product",
                    params={"data_product_id": data_product_id},
                )
                .json()
                .get("role_assignments", [])
            )
            owners = [
                owner.get("user").get("id")
                for owner in roles
                if owner.get("role", {}).get("name", "").lower() == "owner"
            ]
            output_port_payload = {
                "name": "Contact Survey Data Mart",
                "namespace": f"{namespace}-output",
                "description": "Output port for the Contact Survey Data data product",
                "tag_ids": [],
                "access_type": "restricted",
                "lifecycle_id": "00000000-0000-0000-0000-000000000001",
                "owners": owners,
            }

            output_port_url = (
                f"{portal_url}/api/v2/data_products/{data_product_id}/output_ports"
            )
            logging.info(f"Creating data output port at {output_port_url}")

            output_port_response = requests.post(
                output_port_url, json=output_port_payload
            )
            output_port_response.raise_for_status()
            logging.info(
                f"Successfully created data output port for data product {data_product_id}."
            )
        except Exception as e:
            logging.error(f"Failed to auto create output port and tables: {e}")
            if hasattr(e, "response") and e.response is not None:
                logging.error(f"Response body: {e.response.text}")

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

            update_url = f"{portal_url}/api/v2/data_products/{data_product_id}"
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

    # # Optionally create PostgreSQL output port (keeping existing logic)
    # configs = get_platform_service_configurations()
    # postgres_config = next(
    #     (c for c in configs if c.get("service", {}).get("name") == "PostgreSQL"), None
    # )

    # if postgres_config:
    #     platform_id = postgres_config.get("platform", {}).get("id")
    #     service_id = postgres_config.get("service", {}).get("id")
    #     schema_name = data_product_details.get("namespace", "").replace("-", "_")

    #     output_port_payload = {
    #         "name": data_product_details.get("name"),
    #         "namespace": data_product_details.get("namespace"),
    #         "description": data_product_details.get("description"),
    #         "tag_ids": [],
    #         "status": "active",
    #         "sourceAligned": True,
    #         "platform_id": platform_id,
    #         "service_id": service_id,
    #         "configuration": {
    #             "configuration_type": "PostgreSQLDataOutput",
    #             "database": "dpp_demo",
    #             "schema": schema_name,
    #             "entire_schema": True,
    #         },
    #         "result": f"dpp_demo.{schema_name}.*",
    #     }

    #     try:
    #         output_port_url = (
    #             f"{portal_url}/api/v2/data_products/{data_product_id}/data_output"
    #         )
    #         logging.info(f"Creating data output port at {output_port_url}")

    #         output_port_response = requests.post(
    #             output_port_url, json=output_port_payload
    #         )
    #         output_port_response.raise_for_status()
    #         logging.info(
    #             f"Successfully created data output port for data product {data_product_id}."
    #         )
    #     except requests.exceptions.RequestException as e:
    #         logging.error(f"Failed to create data output port: {e}")
    #         if e.response is not None:
    #             logging.error(f"Response body: {e.response.text}")

    return {
        "status": "success",
        "action": "create_data_product",
        "namespace": namespace,
        "s3_location": f"s3://{s3_bucket_name}/{namespace}",
        "project_path": f"/products/{namespace}",
    }


def handle_approve_link(
    data_product_id: str, output_port_id: str, payload: Dict[str, Any]
):
    """
    Handler for approving an input port (consumer access to provider data).
    When approval succeeds, grant the consumer access to the provider's S3 paths.

    Args:
        data_product_id: The provider data product ID (owner of the output port)
        output_port_id: The output port ID being accessed
        payload: Webhook payload containing request/response details
    """
    logging.info(
        f"Handling input port approval for provider {data_product_id}, output port {output_port_id}"
    )
    # Check if the approval was successful (status 200)
    status_code = payload.get("status_code")

    if status_code != 200:
        logging.info(
            f"Approval not successful (status {status_code}), skipping access grant"
        )
        response_data = json.loads(payload.get("response", "{}"))
        return {
            "status": "skipped",
            "action": "approve_input_port",
            "message": f"Approval not successful: {response_data.get('detail', 'Unknown error')}",
        }

    try:
        # Parse the request body to get consumer data product ID
        response = payload.get("response", "{}")
        if isinstance(response, str):
            response = json.loads(response)

        consumer_data_product_id = response.get("consuming_data_product_id")

        if not consumer_data_product_id:
            logging.error("Could not find consuming_data_product_id in request body")
            return {
                "status": "error",
                "message": "Could not find consuming_data_product_id in request body",
            }

        logging.info(f"Consumer data product ID: {consumer_data_product_id}")

        # Fetch provider data product details
        try:
            provider_response = requests.get(
                f"{portal_url}/api/v2/data_products/{data_product_id}"
            )
            provider_response.raise_for_status()
            provider_details = provider_response.json()
            provider_namespace = provider_details.get("namespace")
            logging.info(f"Provider namespace: {provider_namespace}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get provider data product details: {e}")
            return {
                "status": "error",
                "message": f"Failed to get provider details: {str(e)}",
            }

        # Fetch consumer data product details
        try:
            consumer_response = requests.get(
                f"{portal_url}/api/v2/data_products/{consumer_data_product_id}"
            )
            consumer_response.raise_for_status()
            consumer_details = consumer_response.json()
            consumer_namespace = consumer_details.get("namespace")
            logging.info(f"Consumer namespace: {consumer_namespace}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get consumer data product details: {e}")
            return {
                "status": "error",
                "message": f"Failed to get consumer details: {str(e)}",
            }

        # Grant S3 access to consumer by updating their allowed prefixes
        provider_s3_path = f"s3://{s3_bucket_name}/{provider_namespace}"
        consumer_s3_path = f"s3://{s3_bucket_name}/{consumer_namespace}"

        # Update the consumer's allowed prefixes in our credentials store
        if consumer_namespace in credentials_store:
            if (
                provider_namespace
                not in credentials_store[consumer_namespace]["allowed_prefixes"]
            ):
                credentials_store[consumer_namespace]["allowed_prefixes"].append(
                    provider_namespace
                )
                logging.info(
                    f"✅ Access granted! Updated consumer '{consumer_namespace}' allowed prefixes: "
                    f"{credentials_store[consumer_namespace]['allowed_prefixes']}"
                )

                # Update the MinIO user's policy to include the new prefix
                try:
                    create_minio_user_with_policy(
                        consumer_namespace,
                        credentials_store[consumer_namespace]["access_key"],
                        credentials_store[consumer_namespace]["secret_key"],
                        credentials_store[consumer_namespace]["allowed_prefixes"],
                    )
                    logging.info(
                        f"✅ MinIO policy updated for consumer '{consumer_namespace}'"
                    )
                except Exception as e:
                    logging.error(f"Failed to update MinIO policy: {e}", exc_info=True)
                    return {
                        "status": "error",
                        "message": f"Failed to update MinIO policy: {str(e)}",
                    }
            else:
                logging.info(
                    f"Consumer '{consumer_namespace}' already has access to '{provider_namespace}'"
                )
        else:
            logging.warning(
                f"Consumer '{consumer_namespace}' not found in credentials store. "
                f"They may be using minioadmin credentials."
            )

        logging.info(
            f"✅ Access granted: Consumer '{consumer_namespace}' can now read from provider '{provider_namespace}'"
        )
        logging.info(f"   Provider S3 path: {provider_s3_path}")
        logging.info(f"   Consumer S3 path: {consumer_s3_path}")
        logging.info(
            "   Note: In production, this would update MinIO policies via Admin API."
        )

        # For demo purposes, we could update the consumer's .env with a note about available providers
        consumer_project_path = os.path.join(tempplate_output_path, consumer_namespace)

        if os.path.exists(consumer_project_path):
            # Optionally write a file documenting accessible providers
            access_file_path = os.path.join(
                consumer_project_path, "ACCESSIBLE_DATA_PRODUCTS.txt"
            )
            try:
                with open(access_file_path, "a") as f:
                    f.write(f"\n# Approved access: {provider_namespace}\n")
                    f.write(f"# S3 Path: {provider_s3_path}\n")
                    f.write(f"# Granted: {payload.get('timestamp', 'unknown')}\n")
                    f.write(f"# Read from: {provider_s3_path}/staging/*.parquet\n")
                    f.write(f"#            {provider_s3_path}/data_mart/*.parquet\n")

                    # Add info about credentials
                    if consumer_namespace in credentials_store:
                        f.write("\n# Your credentials now grant read access to: \n")
                        for prefix in credentials_store[consumer_namespace][
                            "allowed_prefixes"
                        ]:
                            f.write(f"#   - s3://{s3_bucket_name}/{prefix}/\n")

                logging.info(
                    f"Updated access documentation for consumer: {consumer_namespace}"
                )
            except IOError as e:
                logging.warning(f"Could not write access file: {e}")

        return {
            "status": "success",
            "action": "approve_input_port",
            "provider_namespace": provider_namespace,
            "consumer_namespace": consumer_namespace,
            "provider_s3_path": provider_s3_path,
            "message": f"Consumer '{consumer_namespace}' can now read from '{provider_namespace}'",
        }

    except Exception as e:
        logging.error(f"Error handling input port approval: {e}", exc_info=True)
        return {
            "status": "error",
            "action": "approve_input_port",
            "message": f"Error: {str(e)}",
        }


def handle_approve_link_old(link_id: str, payload: Dict[str, Any]):
    """
    OLD Handler - kept for reference
    Handler for approving a data product link.
    When a link is approved, regenerate credentials for the consumer.
    """
    logging.info(f"Approving link {link_id} with payload: {payload}")

    # Extract link details from payload (the response may contain link info)
    # For this POC, we'll try to get the consumer data product info


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
        compiled_pattern = re.compile(f"^{path_regex}$")
        self.routes.append((method.upper(), compiled_pattern, handler))
        logging.info(f"Registered route: {method.upper()} {path_template}")
        logging.debug(f"  Pattern: {path_regex}")
        logging.debug(f"  Compiled: {compiled_pattern.pattern}")

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
                logging.debug(f"  Trying pattern: {route_pattern.pattern}")
                match = route_pattern.match(url)
                if match:
                    args = match.groups()
                    logging.info(
                        f"✓ Matched route: {handler.__name__} with args: {args}"
                    )
                    response = handler(*args, payload=webhook_payload)
                    return response
                else:
                    logging.debug(f"  No match for pattern: {route_pattern.pattern}")

        return not_found(webhook_payload)


# --- FastAPI App and Route Registration ---


def run_bootstrap_in_background():
    """
    Runs bootstrap in a background thread after ensuring the provisioner is ready.
    This prevents race conditions where webhooks arrive before the server can handle them.
    """
    # Wait a few seconds for the FastAPI server to fully start
    time.sleep(3)

    # Verify provisioner is ready to accept requests
    logging.info("🔍 Verifying provisioner is ready to handle webhooks...")
    max_checks = 20
    for i in range(max_checks):
        try:
            response = requests.get("http://localhost:8090/health", timeout=2)
            if response.status_code == 200:
                logging.info("✅ Provisioner is ready!")
                break
        except Exception:
            pass

        if i < max_checks - 1:
            logging.debug(
                f"   Provisioner not ready yet, waiting... ({i + 1}/{max_checks})"
            )
            time.sleep(1)
    else:
        logging.warning("⚠️  Could not verify provisioner readiness, proceeding anyway")

    # Now run the bootstrap
    try:
        bootstrap_demo_data_product()
    except Exception as e:
        logging.error(f"Bootstrap failed (non-critical): {e}", exc_info=True)


async def startup_event(_: FastAPI):
    """
    Runs on FastAPI application startup.
    Sets up MinIO configuration and schedules demo data product creation.
    """
    logging.info("=" * 60)
    logging.info("Starting Provisioner Service")
    logging.info("=" * 60)

    # Setup MinIO client alias
    setup_mc_alias()

    # Start bootstrap in background thread (after server is ready)
    bootstrap_thread = threading.Thread(
        target=run_bootstrap_in_background, daemon=True, name="BootstrapThread"
    )
    bootstrap_thread.start()
    logging.info("📋 Bootstrap scheduled to run after server is ready")

    logging.info("=" * 60)
    logging.info("Provisioner Ready - Listening for webhooks")
    logging.info("=" * 60)
    yield


app = FastAPI(title="Provisioner Webhook Handler", lifespan=startup_event)

# Global router instance
router = Router()

# Register all routes here to make them easy to find.
# This makes the application more extensible.
logging.info("Registering routes...")

# Create data product - scaffolds new SQLMesh project with S3 configuration
router.add_route("POST", "/api/v2/data_products", handle_create_data_product)

# Approve input port - grants consumer access to provider's S3 data
# Route pattern captures: data_product_id (provider), output_port_id
# Checks status code 200, then fetches both consumer and provider namespaces
router.add_route(
    "POST",
    "/api/v2/data_products/{uuid}/output_ports/{uuid}/input_ports/approve",
    handle_approve_link,
)

# Delete data product - cleanup (placeholder for now)
router.add_route("DELETE", "/api/v2/data_products/{uuid}", handle_delete_data_product)

logging.info("Route registration complete.")


# --- Bootstrap Demo Data Product ---


def bootstrap_demo_data_product():
    """
    Creates the CoMix Survey Data demo product on startup if it doesn't exist.
    This provides a ready-to-use example data product for demonstrations.
    """
    DEMO_NAMESPACE = "comix-survey-data"
    MAX_RETRIES = 30
    RETRY_INTERVAL = 2

    # Wait for portal to be ready
    logging.info("🚀 Bootstrap: Waiting for Data Product Portal to be ready...")
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get("http://localhost:8090/health", timeout=5)
            if response.status_code == 200:
                logging.info("✅ Portal is ready!")
                break
        except Exception:
            pass

        if attempt < MAX_RETRIES - 1:
            logging.info(
                f"   Attempt {attempt + 1}/{MAX_RETRIES} - waiting {RETRY_INTERVAL}s..."
            )
            time.sleep(RETRY_INTERVAL)
    else:
        logging.warning("⚠️  Portal did not become ready, skipping bootstrap")
        return

    # Check if demo data product already exists
    try:
        response = requests.get(f"{portal_url}/api/v2/data_products")
        if response.status_code == 200:
            data_products = response.json().get("data_products", [])
            if any(dp.get("namespace") == DEMO_NAMESPACE for dp in data_products):
                logging.info(
                    f"✅ Demo data product '{DEMO_NAMESPACE}' already exists, skipping bootstrap"
                )
                return
    except Exception as e:
        logging.warning(f"Could not check existing data products: {e}")

    # Create the demo data product
    logging.info(f"📦 Creating demo data product: {DEMO_NAMESPACE}")

    about_html = """
<div class="data-product-about">
  <h2>About CoMix Survey Data</h2>

  <section class="overview">
    <br/><h3>Overview</h3>
    <p/><p>
      The <strong>CoMix Survey Data</strong> product provides comprehensive insights into social contact patterns
      during the COVID-19 pandemic. This dataset is derived from the CoMix social contact survey, which was
      conducted across multiple European countries to understand how people adapted their social behaviors
      in response to public health measures.
    </p>
    <p/><p>
      This data product contains cleaned, validated, and enriched contact survey data that can be used for
      epidemiological modeling, policy analysis, and social science research.
    </p>
  </section>

  <section class="data-collection">
    <br/><h3>Data Collection Methodology</h3>
    <p/><p>
      The CoMix survey was conducted using online questionnaires distributed to representative samples of
      the population in participating countries. Participants were asked to report:
    </p>
    <ul>
      <li><strong>Contact Events:</strong> All social contacts made on the previous day</li>
      <li><strong>Contact Characteristics:</strong> Age, gender, relationship, duration, and location of each contact</li>
      <li><strong>Protective Behaviors:</strong> Use of masks, hand hygiene, and physical distancing measures</li>
      <li><strong>Demographic Information:</strong> Participant age, household composition, employment status</li>
      <li><strong>Contextual Data:</strong> Local COVID-19 measures, infection rates, and policy interventions</li>
    </ul>
    <p/><p>
      Survey waves were conducted regularly throughout 2020-2022, capturing changes in behavior across
      different phases of the pandemic and varying levels of restrictions.
    </p>
  </section>

  <section class="data-structure">
    <br/><h3>Data Structure</h3>
    <p/><p>This data product is organized into the following key datasets:</p>
    <div class="dataset-grid">
      <div class="dataset-card">
        <h4>📊 demographic_data</h4>
        <p/><p>Participant demographics including age groups, household size, employment status, and geographic location.</p>
      </div>
      <div class="dataset-card">
        <h4>🤝 contact_events</h4>
        <p/><p>Detailed contact events with characteristics like duration, location (home, work, leisure), physical contact, and conversation.</p>
      </div>
      <div class="dataset-card">
        <h4>😷 protective_measures</h4>
        <p/><p>Self-reported use of protective behaviors including mask wearing, social distancing, and hand hygiene practices.</p>
      </div>
      <div class="dataset-card">
        <h4>📅 survey_waves</h4>
        <p/><p>Metadata about survey collection periods, response rates, and alignment with policy intervention dates.</p>
      </div>
      <div class="dataset-card">
        <h4>🦠 contextual_data</h4>
        <p/><p>COVID-19 epidemiological indicators, government measures (stringency index), and vaccination rollout timelines.</p>
      </div>
    </div>
  </section>

  <section class="use-cases">
    <br/><h3>Primary Use Cases</h3>
    <ol>
      <li>
        <strong>Epidemiological Modeling:</strong> Parameterize transmission models with empirical contact matrices
        stratified by age, location, and time period.
      </li>
      <li>
        <strong>Policy Impact Assessment:</strong> Evaluate how lockdowns, school closures, and other non-pharmaceutical
        interventions affected social contact patterns.
      </li>
      <li>
        <strong>Behavioral Research:</strong> Analyze factors influencing compliance with public health recommendations
        and protective behavior adoption.
      </li>
      <li>
        <strong>Cross-Country Comparisons:</strong> Compare contact patterns and behavioral responses across different
        countries and policy approaches.
      </li>
      <li>
        <strong>Vulnerable Population Analysis:</strong> Identify contact patterns among elderly populations and other
        high-risk groups.
      </li>
    </ol>
  </section>

  <section class="data-quality">
    <br/><h3>Data Quality & Validation</h3>
    <p/><p>This data product implements comprehensive quality assurance:</p>
    <ul>
      <li>✅ <strong>Input Validation:</strong> All contact records validated against expected ranges and logical constraints</li>
      <li>✅ <strong>Completeness Checks:</strong> Missing data patterns analyzed and documented; imputation strategies applied where appropriate</li>
      <li>✅ <strong>Consistency Verification:</strong> Cross-field validation (e.g., workplace contacts vs. employment status)</li>
      <li>✅ <strong>Outlier Detection:</strong> Statistical methods applied to identify and flag anomalous responses</li>
      <li>✅ <strong>Temporal Consistency:</strong> Longitudinal validation for panel participants</li>
    </ul>
  </section>

  <section class="privacy">
    <br/><h3>Privacy & Ethics</h3>
    <p/><p>
      All data has been anonymized and aggregated in accordance with GDPR requirements. Direct identifiers have
      been removed, and geographic granularity is limited to region-level to prevent re-identification.
      The original survey received ethical approval from institutional review boards in all participating countries.
    </p>
    <p/><p>
      <strong>Access Type:</strong> Restricted - Users must acknowledge data usage terms and cite original sources.
    </p>
  </section>

  <section class="references">
    <br/><h3>References & Attribution</h3>
    <p/><p>This data product is based on the CoMix social contact survey. Publications using this data should cite:</p>
    <blockquote>
      Jarvis CI, Van Zandvoort K, Gimma A, et al. (2020).
      "Quantifying the impact of physical distance measures on the transmission of COVID-19 in the UK."
      <em>BMC Medicine</em> 18, 124.
    </blockquote>
    <p/><p>
      Additional survey documentation and methodology papers are available in the data product's documentation portal.
    </p>
  </section>

  <section class="contact">
    <br/><h3>Support & Contact</h3>
    <p/><p>
      For questions about this data product, methodology clarifications, or access requests, please contact
      the data product team through the Data Product Portal.
    </p>
    <ul>
      <li>📧 Data Product Team: <a href="mailto:data-team@example.com">data-team@example.com</a></li>
      <li>📚 Documentation: Available in the docs/ directory of this data product</li>
      <li>🐛 Report Issues: Use the Data Product Portal issue tracker</li>
    </ul>
  </section>

  <section class="changelog">
    <br/><h3>Version History</h3>
    <ul>
      <li><strong>v1.0.0</strong> (2024-02) - Initial release with data through December 2022</li>
      <li><strong>v1.1.0</strong> (2024-06) - Added vaccination status enrichment and extended protective measures data</li>
      <li><strong>v1.2.0</strong> (2024-11) - Improved data quality checks and added cross-country comparability metrics</li>
    </ul>
  </section>

  <style>
    .data-product-about {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      line-height: 1.6;
      color: #333;
      max-width: 900px;
    }
    .data-product-about h2 {
      color: #2563eb;
      border-bottom: 2px solid #2563eb;
      padding-bottom: 0.5rem;
      margin-top: 2rem;
    }
    .data-product-about h3 {
      color: #1e40af;
      margin-top: 1.5rem;
    }
    .data-product-about section {
      margin-bottom: 2rem;
    }
    .dataset-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1rem;
      margin: 1rem 0;
    }
    .dataset-card {
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      padding: 1rem;
      background: #f9fafb;
    }
    .dataset-card h4 {
      margin-top: 0;
      color: #1f2937;
    }
    .data-product-about blockquote {
      border-left: 4px solid #2563eb;
      padding-left: 1rem;
      margin-left: 0;
      color: #4b5563;
      font-style: italic;
    }
    .data-product-about ul, .data-product-about ol {
      padding-left: 1.5rem;
    }
    .data-product-about li {
      margin-bottom: 0.5rem;
    }
  </style>
</div>
"""

    payload = {
        "name": "CoMix Survey Data",
        "namespace": DEMO_NAMESPACE,
        "description": "COVID-19 social contact survey data capturing behavioral changes during the pandemic across multiple European countries",
        "about": about_html,
        "status": "ACTIVE",
        "type_id": "c25cf2c2-418a-4d1d-a975-c6af61161546",
        "lifecycle_id": "00000000-0000-0000-0000-000000000001",
        "domain_id": "623e6fbf-3a06-434e-995c-b0336e71806e",
        "tag_ids": [],
        "owners": [
            "b72fca38-17ff-4259-a075-5aaa5973343c",
            "d9f3aae2-391e-46c1-aec6-a7ae1114a7da",
        ],
    }

    try:
        response = requests.post(
            f"{portal_url}/api/v2/data_products", json=payload, timeout=10
        )
        response.raise_for_status()
        data = response.json()
        data_product_id = data.get("id")
        logging.info(
            f"✅ Successfully created demo data product '{DEMO_NAMESPACE}' (ID: {data_product_id})"
        )

        response = requests.post(
            f"{portal_url}/api/v2/data_products/{data_product_id}/link_input_ports",
            json={
                "input_ports": ["eb8bb332-b05e-4529-af43-90f69a6a90bb"],
                "justification": "Ingestion data",
            },
        )

        requests.post(
            f"{portal_url}/api/v2/data_products/eb8bb332-b05e-4529-af43-90f69a6a90bc/output_ports/eb8bb332-b05e-4529-af43-90f69a6a90bb/input_ports/approve",
            json={
                "consuming_data_product_id": data_product_id,
            },
        )

        response = requests.post(
            f"{portal_url}/api/v2/data_products/{data_product_id}/output_ports",
            json={
                "name": "Cleaned Respondent Data",
                "namespace": "cleaned-respondent-data",
                "description": "Output port containing cleaned respondent-level data from the CoMix survey, including demographics and contact events",
                "tag_ids": [],
                "about": "<h1>Cleaned Respondent Data</h1><p/><p>This output port provides access to the cleaned and validated respondent-level data from the CoMix survey. It includes demographic information, contact events, protective behaviors, and contextual data for each survey participant.</p><br/><h3>Last Refreshed</h3><p/><p>2026-03-26</p><br/><h3>Schema</h3><ul><li><strong>respondent_id</strong>: Unique identifier for each survey respondent</li><li><strong>age_group</strong>: Age group of the respondent (e.g., 18-29, 30-39)</li><li><strong>household_size</strong>: Number of people in the respondent's household</li><li><strong>employment_status</strong>: Employment status (e.g., employed, unemployed, student)</li><li><strong>geographic_region</strong>: Geographic region of residence</li><li><strong>contact_events</strong>: Nested data structure containing details of each contact event reported by the respondent, including duration, location, physical contact, and conversation details</li><li><strong>protective_measures</strong>: Self-reported use of protective behaviors such as mask wearing and social distancing</li></ul>",
                "access_type": "restricted",
                "lifecycle_id": "00000000-0000-0000-0000-000000000001",
                "owners": [
                    "b72fca38-17ff-4259-a075-5aaa5973343c"  # Assuming this is the admin user
                ],
            },
        )

        response = requests.get(
            f"{portal_url}/api/v2/authz/role_assignments/data_product",
            params={
                "data_product_id": data_product_id,
                "user_id": "b72fca38-17ff-4259-a075-5aaa5973343c",  # admin user
                "role_id": "e43b6f7a-e776-49b2-9b51-117d8644d971",
            },
        )
        requests.put(
            f"{portal_url}/api/v2/authz/role_assignments/data_product/{response.json().get('role_assignments')[0].get('id')}",
            json={
                "data_product_id": data_product_id,
                "user_id": "b72fca38-17ff-4259-a075-5aaa5973343c",
                "role_id": "9ca3bfdd-2919-4190-a8bb-55e9ee7d70dd",
            },
        )

        logging.info(
            "   The provisioner webhook will scaffold the project automatically"
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Failed to create demo data product: {e}")
        if hasattr(e, "response") and e.response is not None:
            logging.error(f"   Response: {e.response.text}")


@app.get("/")
def get_root(request: Request):
    """Basic root endpoint for health checks."""
    logging.debug(f"GET request from {request.client.host}")
    return {"status": "ok"}


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring and readiness probes."""
    return {"status": "healthy", "service": "provisioner"}


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
