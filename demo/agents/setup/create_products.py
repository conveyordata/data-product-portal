"""
Creates the 3 SwiftGear demo data products via the portal API.
Run this after `docker compose up -d` and all services are healthy.
"""

import requests
import sys
import time

PORTAL_URL = "http://localhost:8080"


def wait_for_portal(max_retries=30, delay=2):
    print("Waiting for portal to be ready...")
    for i in range(max_retries):
        try:
            response = requests.get(
                f"{PORTAL_URL}/api/v2/configuration/data_product_lifecycles"
            )
            if response.status_code == 200:
                print("Portal is ready.")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(delay)
    print("Portal did not become ready in time.")
    return False


def get_type_id(name: str) -> str:
    response = requests.get(f"{PORTAL_URL}/api/v2/configuration/data_product_types")
    response.raise_for_status()
    types = response.json().get("data_product_types", [])
    match = next((t for t in types if t["name"] == name), None)
    if not match:
        raise ValueError(f"Data product type '{name}' not found")
    return match["id"]


def get_domain_id(name: str) -> str:
    response = requests.get(f"{PORTAL_URL}/api/v2/configuration/domains")
    response.raise_for_status()
    domains = response.json().get("domains", [])
    match = next((d for d in domains if d["name"] == name), None)
    if not match:
        raise ValueError(f"Domain '{name}' not found")
    return match["id"]


def create_data_product(
    name: str,
    namespace: str,
    description: str,
    about: str,
    type_name: str,
    domain_name: str,
):
    type_id = get_type_id(type_name)
    domain_id = get_domain_id(domain_name)

    payload = {
        "name": name,
        "namespace": namespace,
        "description": description,
        "about": about,
        "type_id": type_id,
        "domain_id": domain_id,
        "tag_ids": [],
    }

    response = requests.post(f"{PORTAL_URL}/api/v2/data_products", json=payload)
    response.raise_for_status()
    dp = response.json()
    print(f"Created data product: {name} (id={dp['id']}, namespace={namespace})")
    return dp


def main():
    if not wait_for_portal():
        sys.exit(1)

    products = [
        {
            "name": "Inventory Snapshot",
            "namespace": "inventory-snapshot",
            "description": "Current and historical inventory levels for all SwiftGear products.",
            "about": (
                "<h3>Value Proposition</h3>"
                "<p>Provides a trusted, daily snapshot of warehouse stock levels across all SKUs. "
                "Enables accurate demand forecasting, stockout prevention, and supply chain optimization.</p>"
                "<h3>Recommended Use Cases</h3>"
                "<ul><li>Monitor current sellable inventory by category</li>"
                "<li>Analyze historical stock trends</li>"
                "<li>Identify slow-moving or retired products</li></ul>"
            ),
            "type_name": "source aligned",
            "domain_name": "Logistics",
        },
        {
            "name": "Sales Transaction Ledger",
            "namespace": "sales-transaction-ledger",
            "description": "Transactional order data, line items, and subscription revenue for SwiftGear.",
            "about": (
                "<h3>Value Proposition</h3>"
                "<p>Single source of truth for all sales transactions. "
                "Powers revenue reporting, commission calculations, and subscription analytics.</p>"
                "<h3>Important Notes</h3>"
                "<p>All monetary values are stored in cents. Divide by 100 for dollar amounts. "
                "Ignore the calculated_total column — it contains legacy errors.</p>"
                "<h3>Recommended Use Cases</h3>"
                "<ul><li>Revenue and AOV analysis</li>"
                "<li>Subscription churn tracking</li>"
                "<li>Order fulfillment monitoring</li></ul>"
            ),
            "type_name": "source aligned",
            "domain_name": "Sales",
        },
        {
            "name": "Customer Demographic Master",
            "namespace": "customer-demographic-master",
            "description": "Master customer records and anonymous web session data for SwiftGear.",
            "about": (
                "<h3>Value Proposition</h3>"
                "<p>Unified customer identity data enabling segmentation, acquisition analysis, "
                "and cross-domain enrichment with sales and subscription data.</p>"
                "<h3>Important Notes</h3>"
                "<p>The acquired_by field references internal admin IDs, not customer IDs. "
                "Web session user_id is anonymous and cannot be directly joined to customers.</p>"
                "<h3>Recommended Use Cases</h3>"
                "<ul><li>Customer segmentation</li>"
                "<li>Acquisition channel analysis</li>"
                "<li>Cross-domain customer enrichment</li></ul>"
            ),
            "type_name": "source aligned",
            "domain_name": "Marketing",
        },
    ]

    for product in products:
        try:
            create_data_product(**product)
        except Exception as e:
            print(f"Failed to create {product['name']}: {e}")
            sys.exit(1)

    print("\nAll data products created successfully.")
    print("The provisioner will now:")
    print("  - Provision DB schemas and users in postgresql-demo")
    print("  - Create OSI and PostgreSQL technical assets")
    print("  - Write agent config YAMLs")
    print("  - Update each product to 'Ready' lifecycle")


if __name__ == "__main__":
    main()
