import os
from typing import Dict

import requests
import yaml

# API key of the data product portal
API_KEY: str = os.getenv("API_KEY", "")
# URL of where to contact the portal API
API_HOST = "https://portal.acme.com"
FOLDER = "./"
proxies: Dict[str, str] = {}

HEADERS = {"x-key": f"{API_KEY}"}
session = requests.Session()
session.proxies = proxies
session.headers.update(HEADERS)


def get_data_products():
    result = session.get(f"{API_HOST}/api/data_products")
    if "correlation_id" in result.json():
        print(result.json())
        exit(1)
    data_products = {}
    for data_product_info in result.json():
        data_product_result = session.get(
            f"{API_HOST}/api/data_products/{data_product_info.get('id')}"
        )
        data_product = data_product_result.json()

        datasets = []
        for dataset_link in data_product.get("dataset_links"):
            if dataset_link.get("status") == "approved":
                datasets.append(dataset_link.get("dataset").get("external_id"))

        # members = {}
        # for member in data_product.get("memberships"):
        #     # EXT is never present in user name?"
        #     role = "admin" if member.get("role") == "owner" else "member"
        #     members[member.get("user").get("email")] = role

        data_products[data_product.get("external_id")] = {
            "description": data_product.get("description"),
            "read_datasets": datasets,
            # "users": members,
        }

    with open(
        os.path.join(
            FOLDER, "config", "data_product_glossary", "data_product_glossary.yaml"
        ),
        "w",
    ) as f:
        yaml.dump(data_products, f, allow_unicode=True)


def get_datasets():
    result = session.get(f"{API_HOST}/api/datasets")

    datasets = {}
    for dataset_info in result.json():
        dataset_result = session.get(
            f"{API_HOST}/api/datasets/{dataset_info.get('id')}"
        )
        dataset = dataset_result.json()

        # owners = []
        # for owner in dataset.get("owners"):
        #     owners.append(owner.get("email"))

        datasets[dataset.get("external_id")] = {
            "data_outputs": [
                data_output_link.get("data_output").get("external_id")
                for data_output_link in dataset.get("data_output_links")
                if data_output_link.get("status") == "approved"
            ],
            # "owner": owners[0],
        }
    with open(
        os.path.join(FOLDER, "config", "data_glossary", "datasets.yaml"), "w"
    ) as f:
        yaml.dump(datasets, f, allow_unicode=True)


def get_data_outputs():
    result = session.get(f"{API_HOST}/api/data_outputs")

    data_outputs = {}
    for data_output_info in result.json():
        platform_id = data_output_info.get("platform_id")
        service_id = data_output_info.get("service_id")
        platform_service_result = session.get(
            f"{API_HOST}/api/platforms/{platform_id}/services/{service_id}"
        )
        platform_service = platform_service_result.json()

        data_outputs[data_output_info.get("external_id")] = {
            platform_service.get("service").get("name"): data_output_info.get(
                "configuration"
            ),
            "owner": data_output_info.get("owner").get("external_id"),
        }

    with open(
        os.path.join(FOLDER, "config", "data_glossary", "data_outputs.yaml"), "w"
    ) as f:
        yaml.dump(data_outputs, f, allow_unicode=True)


def get_environments():
    result = session.get(f"{API_HOST}/api/envs")

    environments = {}
    for environment_info in result.json():
        configs = session.get(
            f"{API_HOST}/api/envs/{environment_info.get('id')}/configs"
        )

        environment_configuration = {}
        for config_info in configs.json():
            environment_configuration[config_info.get("service").get("name")] = (
                config_info.get("config")
            )

        environments[environment_info.get("name")] = environment_configuration

    with open(
        os.path.join(
            FOLDER, "config", "environment_configuration", "environments.yaml"
        ),
        "w",
    ) as f:
        yaml.dump(environments, f, allow_unicode=True)


def generate():
    get_data_products()
    get_datasets()
    get_data_outputs()
    get_environments()


if __name__ == "__main__":
    generate()
