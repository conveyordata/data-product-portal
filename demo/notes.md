# Demo notes

I have DPP running locally on my laptop in this case.

We have done steps 1 to 3:
- Identified domains: marketing, sales and logistics
- First use case is a consumer aligned data product a customer360
- For this we needed 3 source-aligned data products, these have already been created

I have created a simple cookiecutter template for dbt and we are using postgresql as our query engine.

Let's create a new data product:

Name: Marketing Customer 360
Status: Draft
Domain: Marketing
Description: A consolidated view of customer activity, combining customer profiles, order history, and shipment status for marketing analysis
Request access

After creation go through:
- about tab, way to show more info, description is supposed to be short, here can you do a greater explanation
- Usage, currently unimplemented, but at one of our customers they can see here how the data is used, and how often.
- Input ports vs output ports

Build the SQL code:
```jinja
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

```bash
poetry run dbt run --project-dir marketing_customer_360 --profiles-dir marketing_customer_360
```

Show that table is created.

Now ho to output ports and create a new one to share data with the org.
Explain technical assets and how they relate to access rights.
Explain private, public and restricted.

Show marketplace.
