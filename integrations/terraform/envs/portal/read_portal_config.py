import os
from typing import Any

import requests
import yaml

# API key of the data product portal
API_KEY: str = os.getenv("API_KEY", "")
# URL of where to contact the portal API
API_HOST = "https://portal.acme.com"
FOLDER = "./"
proxies: dict[str, str] = {}

HEADERS = {"x-key": f"{API_KEY}"}
session = requests.Session()
session.proxies = proxies
session.headers.update(HEADERS)


# Definitions to allow for values to be exported as quoted strings in the yaml outputs
class QuotedString(str):
    pass


def quoted_scalar(dumper: yaml.Dumper, data: Any):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


yaml.Dumper.add_representer(QuotedString, quoted_scalar)


# Verification of API responses
def verify_response(response: dict[str, Any]):
    if "correlation_id" in response:
        print(response)
        exit(1)


def get_data_products():
    data_products = session.get(f"{API_HOST}/api/data_products").json()
    verify_response(data_products)

    data_products_export = {}
    for data_product_info in data_products:
        data_product = session.get(
            f"{API_HOST}/api/data_products/{data_product_info.get('id')}"
        ).json()
        verify_response(data_product)

        datasets = []
        for dataset_link in data_product.get("dataset_links"):
            if dataset_link.get("status") == "approved":
                datasets.append(dataset_link.get("dataset").get("namespace"))

        members = {}
        for member in data_product.get("memberships"):
            # EXT is never present in user name?"
            role = "admin" if member.get("role") == "owner" else "member"
            members[member.get("user").get("email")] = role

        data_products_export[data_product.get("namespace")] = {
            "description": data_product.get("description"),
            "read_datasets": datasets,
            "users": members,
        }
    with open(
        os.path.join(
            FOLDER, "config", "data_product_glossary", "data_product_glossary.yaml"
        ),
        "w",
    ) as f:
        yaml.dump(data_products_export, f, allow_unicode=True)


def get_datasets():
    datasets = session.get(f"{API_HOST}/api/datasets").json()
    verify_response(datasets)

    datasets_export = {}
    for dataset_info in datasets:
        dataset = session.get(
            f"{API_HOST}/api/datasets/{dataset_info.get('id')}"
        ).json()
        verify_response(dataset)

        owners = []
        for owner in dataset.get("owners"):
            owners.append(owner.get("email"))

        datasets_export[dataset.get("namespace")] = {
            "data_outputs": [
                data_output_link.get("data_output").get("namespace")
                for data_output_link in dataset.get("data_output_links")
                if data_output_link.get("status") == "approved"
            ],
            "owner": owners[0],
        }

    with open(
        os.path.join(FOLDER, "config", "data_glossary", "datasets.yaml"), "w"
    ) as f:
        yaml.dump(datasets_export, f, allow_unicode=True)


def get_data_outputs():
    data_outputs = session.get(f"{API_HOST}/api/data_outputs").json()
    verify_response(data_outputs)

    data_outputs_export = {}
    for data_output_info in data_outputs:
        if data_output_info.get("status") != "active":
            continue

        platform_id = data_output_info.get("platform_id")
        service_id = data_output_info.get("service_id")

        platform_service = session.get(
            f"{API_HOST}/api/platforms/{platform_id}/services/{service_id}"
        ).json()
        verify_response(platform_service)

        data_outputs_export[data_output_info.get("namespace")] = {
            platform_service.get("service")
            .get("name")
            .lower(): data_output_info.get("configuration"),
            "owner": data_output_info.get("owner").get("namespace"),
        }

    with open(
        os.path.join(FOLDER, "config", "data_glossary", "data_outputs.yaml"), "w"
    ) as f:
        yaml.dump(data_outputs_export, f, allow_unicode=True)


def get_environments():
    environments = session.get(f"{API_HOST}/api/envs").json()
    verify_response(environments)

    environments_export = {}
    for environment_info in environments:
        environment = environment_info.get("name")
        environment_id = environment_info.get("id")

        # Fetch environment - platform - service specific configuration
        platform_service_configs = session.get(
            f"{API_HOST}/api/envs/{environment_id}/configs"
        ).json()
        verify_response(platform_service_configs)

        environment_configuration = {}
        for config_info in platform_service_configs:
            platform = config_info.get("platform").get("name").lower()
            platform_id = config_info.get("platform").get("id")
            service = config_info.get("service").get("name").lower()
            service_config = config_info.get("config")

            # Fetch environment - platform specific configuration
            platform_config_info = session.get(
                f"{API_HOST}/api/envs/{environment_id}/platforms/{platform_id}/config"
            ).json()
            verify_response(platform_config_info)

            platform_config = platform_config_info.get("config")
            # Explicitly quote the account ID to avoid Terraform to drop leading zeros
            platform_config["account_id"] = QuotedString(platform_config["account_id"])

            if platform not in environment_configuration:
                environment_configuration[platform] = {
                    **platform_config,
                    service: service_config,
                }
            else:
                environment_configuration[platform][service] = service_config

        environments_export[environment] = environment_configuration

    with open(
        os.path.join(
            FOLDER, "config", "environment_configuration", "environments.yaml"
        ),
        "w",
    ) as f:
        yaml.dump(environments_export, f, allow_unicode=True)


def generate():
    get_data_products()
    get_datasets()
    get_data_outputs()
    get_environments()


if __name__ == "__main__":
    generate()
