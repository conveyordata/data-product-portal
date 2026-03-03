# Data Products

# Running the demo

## Before
Run the following command from the `demo/basic` directory to prepare the demo:

```bash
task prepare-demo
```

## During

### Create new dataproduct

Title: `Marketing Customer 360`
Description: `A consolidated view of customer activity, combining customer profiles, order history, and shipment status for marketing analysis`

### Update the code

Create file `customer_360.sql`

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

### Run the dbt use case

To run the demo case:
```bash
poetry run dbt run --project-dir marketing_customer_360 --profiles-dir marketing_customer_360
```

## After

Cleanup
