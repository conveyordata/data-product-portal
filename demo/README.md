# Demo Scenario: E-Commerce Analytics

This document outlines a demo scenario for the Data Product Portal. The goal is to showcase how the portal can help a company adopt data product thinking. We'll start with raw, operational data sources and use the portal to expose them as well-governed, discoverable data products. Finally, we'll create a new, consumer-aligned data product by combining existing ones.

The demo uses a simple e-commerce model that is easy to recognize. All source data resides in a PostgreSQL database in the `sources` schema. Each data product will be materialized in its own dedicated schema.

## Prerequisites

Before we start the scenario, we need to define the foundational concepts of our imaginary e-commerce business.

### Domains

| Domain | Description |
| --- | --- |
| **Sales** | Responsible for all activities related to sales, customer relationships, and order management. |
| **Marketing** | Focused on customer outreach, promotions, and analyzing customer behavior to drive sales. |
| **Logistics** | Manages inventory, warehousing, and the entire order fulfillment and shipping process. |

### Conceptual Data Model

Our e-commerce platform is based on a few core concepts:

- **Customers**: Individuals or entities who buy products.
- **Products**: The items available for sale.
- **Orders**: A customer's request to purchase one or more products.
- **Shipments**: The process of delivering an order to a customer.

### Operational Sources (in `sources` schema)

These are the raw tables from our operational systems. They are the starting point for our data products.

#### 1. `sources.crm_customers` (from Sales Domain)

This table contains customer information from our CRM system.

| Column | Type | Description |
| --- | --- | --- |
| `id` | `INTEGER` | Unique identifier for the customer. |
| `first_name` | `VARCHAR(50)` | Customer's first name. |
| `last_name` | `VARCHAR(50)` | Customer's last name. |
| `email` | `VARCHAR(100)` | Customer's email address. |
| `signup_date` | `TIMESTAMP` | When the customer created their account. |

#### 2. `sources.erp_orders` (from Sales Domain)

This table holds order data from our ERP system.

| Column | Type | Description |
| --- | --- | --- |
| `order_id` | `INTEGER` | Unique identifier for the order. |
| `customer_id` | `INTEGER` | Foreign key to `crm_customers.id`. |
| `order_date` | `TIMESTAMP` | The date and time the order was placed. |
| `total_amount` | `DECIMAL(10, 2)` | The total value of the order. |

#### 3. `sources.wms_shipments` (from Logistics Domain)

This table contains shipment information from our Warehouse Management System.

| Column | Type | Description |
| --- | --- | --- |
| `shipment_id` | `INTEGER` | Unique identifier for the shipment. |
| `order_ref` | `INTEGER` | Foreign key to `erp_orders.order_id`. |
| `shipped_date` | `TIMESTAMP` | When the order was shipped from the warehouse. |
| `delivery_status`| `VARCHAR(20)` | Current status of the delivery (e.g., 'Shipped', 'In Transit', 'Delivered'). |

## Scenario Steps

Now we'll walk through the process of creating data products using the portal.

### 1. Expose Sources as Source-Aligned Data Products

Our first goal is to make the raw operational data available as trusted, documented, and easily accessible data products. We create a 1-to-1 mapping for each source table.

#### Data Product 1: `Sales CRM Customers`

- **Owner**: Sales Domain
- **Schema**: `sales_crm`
- **Output Port**: `customers`
- **Description**: "Provides a clean, trusted view of customer account information, sourced directly from our CRM."

**Table: `sales_crm.customers`**

| Column | Type | Description |
| --- | --- | --- |
| `id` | `INTEGER` | Unique identifier for the customer. |
| `first_name` | `VARCHAR(50)` | Customer's first name. |
| `last_name` | `VARCHAR(50)` | Customer's last name. |
| `email` | `VARCHAR(100)` | Customer's email address. |
| `signup_date` | `TIMESTAMP` | When the customer created their account. |

#### Data Product 2: `Sales ERP Orders`

- **Owner**: Sales Domain
- **Schema**: `sales_erp`
- **Output Port**: `orders`
- **Description**: "Provides real-time order data from our ERP system."

**Table: `sales_erp.orders`**

| Column | Type | Description |
| --- | --- | --- |
| `order_id` | `INTEGER` | Unique identifier for the order. |
| `customer_id` | `INTEGER` | Foreign key to `sales_crm.customers.id`. |
| `order_date` | `TIMESTAMP` | The date and time the order was placed. |
| `total_amount` | `DECIMAL(10, 2)` | The total value of the order. |

#### Data Product 3: `Logistics WMS Shipments`

- **Owner**: Logistics Domain
- **Schema**: `logistics_wms`
- **Output Port**: `shipments`
- **Description**: "Tracks order shipment and delivery status from the warehouse."

**Table: `logistics_wms.shipments`**

| Column | Type | Description |
| --- | --- | --- |
| `shipment_id` | `INTEGER` | Unique identifier for the shipment. |
| `order_ref` | `INTEGER` | Foreign key to `sales_erp.orders.order_id`. |
| `shipped_date` | `TIMESTAMP` | When the order was shipped from the warehouse. |
| `delivery_status`| `VARCHAR(20)` | Current status of the delivery. |

### 2. Create a Consumer-Aligned Data Product

The Marketing team wants to run a campaign for our most loyal customers. To do this, they need a single view of customer, order, and shipment information. They don't want to deal with joining tables from three different systems. We'll create a new data product tailored to their needs.

#### Data Product 4: `Marketing Customer 360`

- **Owner**: Marketing Domain
- **Schema**: `marketing_360`
- **Output Port**: `customer_activity`
- **Description**: "A consolidated view of customer activity, combining customer profiles, order history, and shipment status for marketing analysis."
- **Input Data Products**:
  - `Sales CRM Customers`
  - `Sales ERP Orders`
  - `Logistics WMS Shipments`

This data product is created by joining the tables from the input data products to create a new, aggregated table.

**Model SQL:**
```sql
WITH customers AS (
    SELECT * FROM {{ source('sales_crm_customers', 'customers') }}
),

orders AS (
    SELECT * FROM {{ source('sales_erp_orders', 'orders') }}
),

shipments AS (
    SELECT * FROM {{ source('logistics_wms_shipments', 'shipments') }}
)

SELECT
    c.id AS customer_id,
    c.first_name,
    c.last_name,
    c.email AS customer_email,
    o.order_id,
    o.order_date,
    o.total_amount AS order_total,
    s.shipment_id,
    s.shipped_date,
    s.delivery_status AS shipment_status
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
LEFT JOIN shipments s ON o.order_id = s.order_ref
```

**Table: `marketing_360.customer_activity`**

| Column | Type | Description |
| --- | --- | --- |
| `customer_id` | `INTEGER` | Unique identifier for the customer. |
| `customer_name` | `VARCHAR(101)` | Full name of the customer. |
| `customer_email` | `VARCHAR(100)` | Customer's email address. |
| `account_age_days`| `INTEGER` | Number of days since the customer signed up. |
| `order_id` | `INTEGER` | The unique ID of the order. |
| `order_total` | `DECIMAL(10, 2)` | The total value of the order. |
| `days_from_order_to_ship` | `INTEGER` | The number of days between placing the order and shipment. |
| `delivery_status`| `VARCHAR(20)` | The latest known delivery status of the order. |
