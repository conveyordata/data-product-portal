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
