# /// script
# requires-python = ">=3.12"
# dependencies = ["requests"]
# ///
"""
Creates the 3 SwiftGear demo data products, their output ports, and curated queries via the portal API.
Run this after `docker compose up -d` and all services are healthy.
"""

import requests
import sys
import time
import traceback
from typing import Any

PORTAL_URL = "http://localhost:8080"

# john.scientist is the admin user seeded in portal_seed.sql
OWNER_ID = "b72fca38-17ff-4259-a075-5aaa5973343c"


# ---------------------------------------------------------------------------
# Portal readiness
# ---------------------------------------------------------------------------


def wait_for_portal(max_retries=30, delay=2):
    print("Waiting for portal to be ready...")
    for _ in range(max_retries):
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


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


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


def get_lifecycle_id(name: str) -> str:
    response = requests.get(
        f"{PORTAL_URL}/api/v2/configuration/data_product_lifecycles"
    )
    response.raise_for_status()
    lifecycles = response.json().get("data_product_life_cycles", [])
    match = next((lc for lc in lifecycles if lc["name"] == name), None)
    if not match:
        raise ValueError(f"Lifecycle '{name}' not found")
    return match["id"]


# ---------------------------------------------------------------------------
# Data product creation
# ---------------------------------------------------------------------------


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
    lifecycle_id = get_lifecycle_id("Draft")

    payload = {
        "name": name,
        "namespace": namespace,
        "description": description,
        "about": about,
        "type_id": type_id,
        "domain_id": domain_id,
        "lifecycle_id": lifecycle_id,
        "owners": [OWNER_ID],
        "tag_ids": [],
    }

    response = requests.post(f"{PORTAL_URL}/api/v2/data_products", json=payload)
    response.raise_for_status()
    dp = response.json()
    print(f"  Created data product: {name} (id={dp['id']})")
    return dp


# ---------------------------------------------------------------------------
# Wait for provisioner to create technical assets
# ---------------------------------------------------------------------------


def wait_for_technical_assets(dp_id: str, count: int = 2, max_retries=30, delay=2):
    """Poll until the data product has at least `count` technical assets."""
    print(f"  Waiting for provisioner to create {count} technical assets...")
    for _ in range(max_retries):
        response = requests.get(
            f"{PORTAL_URL}/api/v2/data_products/{dp_id}/technical_assets"
        )
        response.raise_for_status()
        tas = response.json().get("technical_assets", [])
        if len(tas) >= count:
            ids = [ta["id"] for ta in tas]
            print(f"  Found {len(tas)} technical assets.")
            return ids
        time.sleep(delay)
    raise TimeoutError(f"Data product {dp_id} did not get {count} TAs in time.")


# ---------------------------------------------------------------------------
# Output port creation + TA linking
# ---------------------------------------------------------------------------


def create_output_port(
    dp_id: str,
    name: str,
    namespace: str,
    description: str,
    about: str,
    access_type: str,  # "public" | "restricted" | "private"
) -> str:
    payload = {
        "name": name,
        "namespace": namespace,
        "description": description,
        "about": about,
        "access_type": access_type,
        "owners": [OWNER_ID],
        "tag_ids": [],
    }
    response = requests.post(
        f"{PORTAL_URL}/api/v2/data_products/{dp_id}/output_ports", json=payload
    )
    response.raise_for_status()
    op_id = response.json()["id"]
    print(f"  Created output port: {name} [{access_type}] (id={op_id})")
    return op_id


def link_and_approve_ta(dp_id: str, op_id: str, ta_id: str):
    """Request and immediately approve a TA link on an output port."""
    add_url = f"{PORTAL_URL}/api/v2/data_products/{dp_id}/output_ports/{op_id}/technical_assets/add"
    requests.post(add_url, json={"technical_asset_id": ta_id}).raise_for_status()

    approve_url = f"{PORTAL_URL}/api/v2/data_products/{dp_id}/output_ports/{op_id}/technical_assets/approve_link_request"
    requests.post(approve_url, json={"technical_asset_id": ta_id}).raise_for_status()


def set_curated_queries(dp_id: str, op_id: str, queries: list[dict]):
    url = f"{PORTAL_URL}/api/v2/data_products/{dp_id}/output_ports/{op_id}/curated_queries"
    requests.put(url, json={"curated_queries": queries}).raise_for_status()
    print(f"  Added {len(queries)} curated queries.")


# ---------------------------------------------------------------------------
# Output port definitions per data product
# ---------------------------------------------------------------------------

OUTPUT_PORTS: dict[str, Any] = {
    "inventory-snapshot": {
        "name": "Inventory Data",
        "namespace": "inventory-data",
        "description": "Daily stock snapshots and historical inventory levels by SKU and warehouse.",
        "access_type": "public",
        "about": (
            "<h3>Connection Details</h3>"
            "<table><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>"
            "<tr><td>Host</td><td>postgresql-demo</td></tr>"
            "<tr><td>Port</td><td>5432</td></tr>"
            "<tr><td>Database</td><td>dpp_demo</td></tr>"
            "<tr><td>Schema</td><td>inventory_snapshot</td></tr>"
            "<tr><td>Access</td><td>Public — no approval required. A read-only user scoped to this schema is provided upon request.</td></tr>"
            "</tbody></table>"
            "<p></p>"
            "<h3>Tables</h3>"
            "<p></p>"
            "<h4>inventory_latest</h4>"
            "<p>Current daily snapshot of warehouse stock. Use this table for all current-stock questions.</p>"
            "<table><thead><tr><th>Column</th><th>Type</th><th>Description</th></tr></thead><tbody>"
            "<tr><td>sku</td><td>text</td><td>Stock Keeping Unit. Camping products follow <code>CAMP-*</code> prefix convention.</td></tr>"
            "<tr><td>qty_oh</td><td>integer</td><td>Quantity on hand — current units available in the warehouse.</td></tr>"
            "<tr><td>warehouse_id</td><td>integer</td><td>Warehouse location identifier.</td></tr>"
            "</tbody></table>"
            "<p></p>"
            "<h4>stock_levels</h4>"
            "<p>Historical log of stock-level snapshots over time. Includes retired items — always filter them out for sellable counts.</p>"
            "<table><thead><tr><th>Column</th><th>Type</th><th>Description</th></tr></thead><tbody>"
            "<tr><td>sku</td><td>text</td><td>Stock Keeping Unit.</td></tr>"
            "<tr><td>qty_oh</td><td>integer</td><td>Quantity on hand at snapshot time.</td></tr>"
            "<tr><td>is_retired</td><td>boolean</td><td>True if this item is no longer for sale. Always filter <code>WHERE is_retired = false</code> for sellable inventory.</td></tr>"
            "<tr><td>captured_at</td><td>timestamp</td><td>When this snapshot was recorded.</td></tr>"
            "</tbody></table>"
            "<p></p>"
            "<h3>Semantic Model Highlights</h3>"
            "<ul>"
            "<li>Use <code>inventory_latest</code> for current stock — it is inherently filtered to active items.</li>"
            "<li>For historical analysis on <code>stock_levels</code>, always add <code>WHERE is_retired = false</code> to exclude discontinued products.</li>"
            "<li>Sellable inventory metric: <code>SUM(qty_oh)</code> on <code>inventory_latest</code>.</li>"
            "<li>Camping gear filter: <code>sku LIKE 'CAMP-%'</code>.</li>"
            "</ul>"
        ),
        "curated_queries": [
            {
                "title": "Current stock by warehouse",
                "description": "Total units on hand grouped by warehouse location.",
                "query_text": (
                    "SELECT\n"
                    "  warehouse_id,\n"
                    "  SUM(qty_oh) AS total_units\n"
                    "FROM inventory_snapshot.inventory_latest\n"
                    "GROUP BY warehouse_id\n"
                    "ORDER BY total_units DESC;"
                ),
            },
            {
                "title": "Low stock alert — SKUs under 10 units",
                "description": "Identify SKUs at risk of stockout across all warehouses.",
                "query_text": (
                    "SELECT\n"
                    "  sku,\n"
                    "  SUM(qty_oh) AS total_units\n"
                    "FROM inventory_snapshot.inventory_latest\n"
                    "GROUP BY sku\n"
                    "HAVING SUM(qty_oh) < 10\n"
                    "ORDER BY total_units;"
                ),
            },
            {
                "title": "Camping gear inventory",
                "description": "Current stock for all camping category SKUs (CAMP-* prefix).",
                "query_text": (
                    "SELECT\n"
                    "  sku,\n"
                    "  SUM(qty_oh) AS units_on_hand\n"
                    "FROM inventory_snapshot.inventory_latest\n"
                    "WHERE sku LIKE 'CAMP-%'\n"
                    "GROUP BY sku\n"
                    "ORDER BY units_on_hand DESC;"
                ),
            },
            {
                "title": "Historical stock trend (last 30 days)",
                "description": "Daily sellable stock totals over the past 30 days. Retired items are excluded.",
                "query_text": (
                    "SELECT\n"
                    "  captured_at::date AS date,\n"
                    "  SUM(qty_oh) AS sellable_units\n"
                    "FROM inventory_snapshot.stock_levels\n"
                    "WHERE is_retired = false\n"
                    "  AND captured_at >= NOW() - INTERVAL '30 days'\n"
                    "GROUP BY date\n"
                    "ORDER BY date;"
                ),
            },
        ],
    },
    "sales-transaction-ledger": {
        "name": "Sales & Revenue Data",
        "namespace": "sales-revenue-data",
        "description": "Transactional orders, line items, and subscription revenue for revenue reporting and analytics.",
        "access_type": "public",
        "about": (
            "<h3>Connection Details</h3>"
            "<table><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>"
            "<tr><td>Host</td><td>postgresql-demo</td></tr>"
            "<tr><td>Port</td><td>5432</td></tr>"
            "<tr><td>Database</td><td>dpp_demo</td></tr>"
            "<tr><td>Schema</td><td>sales_transaction_ledger</td></tr>"
            "<tr><td>Access</td><td>Restricted — request access through the portal. You will receive a dedicated read-only user scoped to this schema.</td></tr>"
            "</tbody></table>"
            "<p></p>"
            "<h3>Tables</h3>"
            "<p></p>"
            "<h4>orders</h4>"
            "<p>Order headers — one row per customer order.</p>"
            "<table><thead><tr><th>Column</th><th>Type</th><th>Description</th></tr></thead><tbody>"
            "<tr><td>order_id</td><td>uuid</td><td>Primary key.</td></tr>"
            "<tr><td>customer_id</td><td>uuid</td><td>FK to <code>customer_demographic_master.customers.id</code>.</td></tr>"
            "<tr><td>total_amount</td><td>integer</td><td>Order total <strong>in cents</strong>. Use <code>total_amount / 100.0</code> for dollars. Never use <code>calculated_total</code> — it contains legacy errors.</td></tr>"
            "<tr><td>status</td><td>text</td><td>Order status. A NULL status with a non-null <code>created_at</code> indicates an order in processing.</td></tr>"
            "<tr><td>created_at</td><td>timestamp</td><td>Order creation time.</td></tr>"
            "<tr><td>shipped_at</td><td>timestamp</td><td>Shipment timestamp (nullable).</td></tr>"
            "</tbody></table>"
            "<p></p>"
            "<h4>order_items</h4>"
            "<p>Line items — one row per SKU per order.</p>"
            "<table><thead><tr><th>Column</th><th>Type</th><th>Description</th></tr></thead><tbody>"
            "<tr><td>item_id</td><td>uuid</td><td>Primary key.</td></tr>"
            "<tr><td>order_id</td><td>uuid</td><td>FK to <code>orders.order_id</code>.</td></tr>"
            "<tr><td>sku</td><td>text</td><td>Product identifier (matches <code>inventory_snapshot.inventory_latest.sku</code>).</td></tr>"
            "<tr><td>price_cents</td><td>integer</td><td>Unit price in cents. Use <code>price_cents / 100.0</code> for dollars.</td></tr>"
            "<tr><td>quantity</td><td>integer</td><td>Units purchased.</td></tr>"
            "</tbody></table>"
            "<p></p>"
            "<h4>recurring_revenue</h4>"
            "<p>Subscription records — one row per subscription lifecycle.</p>"
            "<table><thead><tr><th>Column</th><th>Type</th><th>Description</th></tr></thead><tbody>"
            "<tr><td>subscription_id</td><td>uuid</td><td>Primary key.</td></tr>"
            "<tr><td>mrr</td><td>integer</td><td>Monthly recurring revenue in cents. Use <code>COALESCE(mrr, 0) / 100.0</code>.</td></tr>"
            "<tr><td>status</td><td>text</td><td>ACTIVE, TRIAL, or CANCELED.</td></tr>"
            "<tr><td>started_at</td><td>timestamp</td><td>Subscription start date. Renewal: <code>started_at + INTERVAL '1 year'</code>.</td></tr>"
            "<tr><td>ended_at</td><td>timestamp</td><td>Cancellation date (nullable).</td></tr>"
            "</tbody></table>"
            "<p></p>"
            "<h3>Semantic Model Highlights</h3>"
            "<ul>"
            "<li><strong>All monetary values are stored in cents.</strong> Always divide by 100.0 for dollar amounts.</li>"
            "<li>Never use <code>calculated_total</code> — it is a legacy column with known errors. Use <code>total_amount / 100.0</code>.</li>"
            "<li>Churn rate: <code>COUNT(CANCELED)::float / NULLIF(COUNT(non-TRIAL), 0)</code>.</li>"
            "<li>Average order value: <code>SUM(total_amount) / 100.0 / COUNT(DISTINCT order_id)</code>.</li>"
            "</ul>"
        ),
        "curated_queries": [
            {
                "title": "Total revenue (all time)",
                "description": "Sum of all order amounts in dollars. Excludes the legacy calculated_total column.",
                "query_text": (
                    "SELECT\n"
                    "  SUM(total_amount) / 100.0 AS total_revenue_usd\n"
                    "FROM sales_transaction_ledger.orders;"
                ),
            },
            {
                "title": "Average order value",
                "description": "Mean order value in dollars across all orders.",
                "query_text": (
                    "SELECT\n"
                    "  (SUM(total_amount) / 100.0) / COUNT(DISTINCT order_id) AS avg_order_value_usd\n"
                    "FROM sales_transaction_ledger.orders;"
                ),
            },
            {
                "title": "Top 10 SKUs by revenue",
                "description": "Best-selling products ranked by total line-item revenue.",
                "query_text": (
                    "SELECT\n"
                    "  sku,\n"
                    "  SUM(price_cents * quantity) / 100.0 AS revenue_usd\n"
                    "FROM sales_transaction_ledger.order_items\n"
                    "GROUP BY sku\n"
                    "ORDER BY revenue_usd DESC\n"
                    "LIMIT 10;"
                ),
            },
            {
                "title": "Monthly recurring revenue (active subscriptions)",
                "description": "Total MRR in dollars from all currently active subscriptions.",
                "query_text": (
                    "SELECT\n"
                    "  SUM(COALESCE(mrr, 0)) / 100.0 AS total_mrr_usd\n"
                    "FROM sales_transaction_ledger.recurring_revenue\n"
                    "WHERE status = 'ACTIVE';"
                ),
            },
            {
                "title": "Subscription churn rate",
                "description": "Ratio of canceled subscriptions to all non-trial subscriptions. Excludes trial accounts.",
                "query_text": (
                    "SELECT\n"
                    "  COUNT(CASE WHEN status = 'CANCELED' THEN 1 END)::float\n"
                    "    / NULLIF(COUNT(CASE WHEN status != 'TRIAL' THEN 1 END), 0)\n"
                    "    AS churn_rate\n"
                    "FROM sales_transaction_ledger.recurring_revenue;"
                ),
            },
        ],
    },
    "customer-demographic-master": {
        "name": "Customer Records",
        "namespace": "customer-records",
        "description": "Master customer identities and anonymous web session logs for segmentation and acquisition analysis.",
        "access_type": "public",
        "about": (
            "<h3>Connection Details</h3>"
            "<table><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>"
            "<tr><td>Host</td><td>postgresql-demo</td></tr>"
            "<tr><td>Port</td><td>5432</td></tr>"
            "<tr><td>Database</td><td>dpp_demo</td></tr>"
            "<tr><td>Schema</td><td>customer_demographic_master</td></tr>"
            "<tr><td>Access</td><td>Restricted — contains PII. Request access through the portal. You will receive a read-only user scoped to this schema.</td></tr>"
            "</tbody></table>"
            "<p></p>"
            "<h3>Tables</h3>"
            "<p></p>"
            "<h4>customers</h4>"
            "<p>Master customer records — one row per registered SwiftGear customer.</p>"
            "<table><thead><tr><th>Column</th><th>Type</th><th>Description</th></tr></thead><tbody>"
            "<tr><td>id</td><td>uuid</td><td>Primary key. Matches <code>customer_id</code> in <code>sales_transaction_ledger.orders</code> for cross-domain joins.</td></tr>"
            "<tr><td>full_name</td><td>text</td><td>Customer full name (PII).</td></tr>"
            "<tr><td>email</td><td>text</td><td>Customer email address (PII).</td></tr>"
            "<tr><td>acquired_by</td><td>integer</td><td>Internal admin ID of the staff member who acquired this customer. <strong>Do not join this to <code>customers.id</code></strong> — it is not a customer reference.</td></tr>"
            "<tr><td>signup_date</td><td>date</td><td>Date the customer registered.</td></tr>"
            "</tbody></table>"
            "<p></p>"
            "<h4>web_sessions</h4>"
            "<p>Anonymous web traffic logs. Cannot be directly joined to customer records.</p>"
            "<table><thead><tr><th>Column</th><th>Type</th><th>Description</th></tr></thead><tbody>"
            "<tr><td>session_id</td><td>uuid</td><td>Primary key.</td></tr>"
            "<tr><td>user_id</td><td>uuid</td><td>Anonymous session UUID — <strong>not</strong> a customer ID. Cannot be joined to <code>customers.id</code> without a session-identity mapping table (not available in this product).</td></tr>"
            "<tr><td>page_path</td><td>text</td><td>URL path viewed during the session.</td></tr>"
            "<tr><td>viewed_at</td><td>timestamp</td><td>Session timestamp.</td></tr>"
            "</tbody></table>"
            "<p></p>"
            "<h3>Semantic Model Highlights</h3>"
            "<ul>"
            "<li><code>acquired_by</code> is an internal admin ID — never join it to <code>customers.id</code> or any customer-facing key.</li>"
            "<li><code>web_sessions.user_id</code> is an anonymous UUID. It cannot be resolved to a customer without a mapping table that does not exist in this product.</li>"
            "<li>Marketing channel attribution is <strong>not possible</strong> from <code>web_sessions</code> — UTM parameters and referral sources are absent.</li>"
            "<li>To identify active customers, join to <code>sales_transaction_ledger.orders</code> on <code>customers.id = orders.customer_id</code> (requires access to the Sales data product).</li>"
            "</ul>"
        ),
        "curated_queries": [
            {
                "title": "Total registered customers",
                "description": "Count of all customer records in the master table.",
                "query_text": (
                    "SELECT COUNT(*) AS total_customers\n"
                    "FROM customer_demographic_master.customers;"
                ),
            },
            {
                "title": "New signups by month (last 12 months)",
                "description": "Monthly customer acquisition trend over the past year.",
                "query_text": (
                    "SELECT\n"
                    "  DATE_TRUNC('month', signup_date) AS month,\n"
                    "  COUNT(*) AS new_customers\n"
                    "FROM customer_demographic_master.customers\n"
                    "WHERE signup_date >= NOW() - INTERVAL '12 months'\n"
                    "GROUP BY month\n"
                    "ORDER BY month;"
                ),
            },
            {
                "title": "Top 10 most visited pages",
                "description": "Highest-traffic pages based on anonymous session counts.",
                "query_text": (
                    "SELECT\n"
                    "  page_path,\n"
                    "  COUNT(*) AS session_count\n"
                    "FROM customer_demographic_master.web_sessions\n"
                    "GROUP BY page_path\n"
                    "ORDER BY session_count DESC\n"
                    "LIMIT 10;"
                ),
            },
            {
                "title": "Top customers by order count (cross-domain)",
                "description": (
                    "Customers ranked by number of orders placed. "
                    "Requires approved access to both this product and Sales Transaction Ledger."
                ),
                "query_text": (
                    "SELECT\n"
                    "  c.email,\n"
                    "  c.full_name,\n"
                    "  COUNT(o.order_id) AS total_orders\n"
                    "FROM customer_demographic_master.customers c\n"
                    "JOIN sales_transaction_ledger.orders o ON c.id = o.customer_id\n"
                    "GROUP BY c.email, c.full_name\n"
                    "ORDER BY total_orders DESC\n"
                    "LIMIT 10;"
                ),
            },
        ],
    },
}

# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

PRODUCTS = [
    {
        "name": "Inventory Snapshot",
        "namespace": "inventory-snapshot",
        "description": "Current and historical inventory levels for all SwiftGear products.",
        "about": (
            "<h3>Value Proposition</h3>"
            "<p>Provides a trusted, daily snapshot of warehouse stock levels across all SKUs. "
            "Enables accurate demand forecasting, stockout prevention, and supply chain optimization.</p>"
            "<p></p>"
            "<h3>Recommended Use Cases</h3>"
            "<ul>"
            "<li>Logistics: Monitor current sellable inventory by SKU and warehouse.</li>"
            "<li>Operations: Identify slow-moving or retired products before they affect fulfilment.</li>"
            "<li>Supply Chain: Analyse historical stock trends to improve reorder strategies.</li>"
            "</ul>"
            "<p></p>"
            "<h3>Terms of Use</h3>"
            "<ul>"
            "<li>Usage: Approved for internal supply chain, logistics, and operations analytics.</li>"
            "<li>Limitations: Not authorised for external reporting. Stock data must not be shared outside the organisation without prior approval.</li>"
            "</ul>"
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
            "<p>Single source of truth for all SwiftGear sales transactions. "
            "Powers revenue reporting, commission calculations, and subscription analytics across the organisation.</p>"
            "<p></p>"
            "<h3>Recommended Use Cases</h3>"
            "<ul>"
            "<li>Finance: Revenue and average order value analysis.</li>"
            "<li>Product: Subscription churn tracking and MRR reporting.</li>"
            "<li>Operations: Order fulfilment monitoring and SLA compliance.</li>"
            "</ul>"
            "<p></p>"
            "<h3>Terms of Use</h3>"
            "<ul>"
            "<li>Usage: Approved for internal revenue reporting, commission calculations, and subscription analytics.</li>"
            "<li>Limitations: All monetary values are stored in cents — always divide by 100.0 before reporting. "
            "The <code>calculated_total</code> column is deprecated and must not be used.</li>"
            "</ul>"
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
            "<p></p>"
            "<h3>Recommended Use Cases</h3>"
            "<ul>"
            "<li>Marketing: Customer segmentation for email campaigns and loyalty programmes.</li>"
            "<li>Analytics: Acquisition trend analysis and new-customer reporting.</li>"
            "<li>Data Science: Cross-domain enrichment by joining to sales and subscription data.</li>"
            "</ul>"
            "<p></p>"
            "<h3>Terms of Use</h3>"
            "<ul>"
            "<li>Usage: Approved for internal analytics, marketing automation, and customer support workflows.</li>"
            "<li>Limitations: Contains PII (name, email). Handling must strictly adhere to the corporate GDPR compliance framework. "
            "Not authorised for external sharing or regulatory reporting without a signed DPA.</li>"
            "</ul>"
        ),
        "type_name": "source aligned",
        "domain_name": "Marketing",
    },
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def provision_product(product: dict):
    namespace = product["namespace"]
    print(f"\n[{product['name']}]")

    dp = create_data_product(**product)
    dp_id = dp["id"]

    # Wait for provisioner to create the OSI + PostgreSQL technical assets
    ta_ids = wait_for_technical_assets(dp_id, count=2)

    # Create the output port
    op_cfg = OUTPUT_PORTS[namespace]
    op_id = create_output_port(
        dp_id=dp_id,
        name=op_cfg["name"],
        namespace=op_cfg["namespace"],
        description=op_cfg["description"],
        about=op_cfg["about"],
        access_type=op_cfg["access_type"],
    )

    # Link and approve both technical assets
    for ta_id in ta_ids:
        link_and_approve_ta(dp_id, op_id, ta_id)
    print(f"  Linked and approved {len(ta_ids)} technical assets to output port.")

    # Set curated queries
    set_curated_queries(dp_id, op_id, op_cfg["curated_queries"])


def main():
    if not wait_for_portal():
        sys.exit(1)

    for product in PRODUCTS:
        try:
            provision_product(product)
        except Exception:
            print(f"Failed to provision {product['name']}:")
            traceback.print_exc()
            sys.exit(1)

    print(
        "\nAll data products, output ports, and curated queries created successfully."
    )
    print("The provisioner has:")
    print("  - Provisioned DB schemas and users in postgresql-demo")
    print("  - Created OSI and PostgreSQL technical assets")
    print("  - Written agent config YAMLs")
    print("  - Updated each product to 'Ready' lifecycle")


if __name__ == "__main__":
    main()
