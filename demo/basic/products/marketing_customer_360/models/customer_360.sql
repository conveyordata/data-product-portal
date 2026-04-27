WITH customers AS (
    SELECT * FROM {{ source('sales_crm_customers', 'customers') }}
),

orders AS (
    SELECT
        customer_id,
        COUNT(order_id)          AS total_orders,
        SUM(total_amount)        AS total_revenue,
        MAX(order_date)          AS last_order_date
    FROM {{ source('sales_erp_orders', 'orders') }}
    GROUP BY customer_id
),

shipments AS (
    SELECT DISTINCT ON (o.customer_id)
        o.customer_id,
        s.delivery_status        AS last_shipment_status
    FROM {{ source('sales_erp_orders', 'orders') }} o
    JOIN {{ source('logistics_wms_shipments', 'shipments') }} s
        ON o.order_id = s.order_ref
    ORDER BY o.customer_id, s.shipped_date DESC
)

SELECT
    c.id                                                        AS customer_id,
    c.first_name,
    c.last_name,
    c.email,
    c.signup_date,
    COALESCE(o.total_orders, 0)                                 AS total_orders,
    COALESCE(o.total_revenue, 0)                                AS total_revenue,
    o.last_order_date,
    s.last_shipment_status,
    CASE
        WHEN o.total_orders >= 10 AND o.total_revenue >= 1000   THEN 'Champions'
        WHEN o.total_orders >= 5  AND o.total_revenue >= 500    THEN 'Loyal Customers'
        WHEN o.last_order_date >= CURRENT_DATE - INTERVAL '30 days' THEN 'Recent'
        WHEN o.last_order_date >= CURRENT_DATE - INTERVAL '90 days' THEN 'At Risk'
        ELSE 'Churned'
    END                                                         AS rfm_segment
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
LEFT JOIN shipments s ON c.id = s.customer_id
