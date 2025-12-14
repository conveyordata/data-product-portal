-- Drop schema if it exists to ensure a clean slate
DROP SCHEMA IF EXISTS sources CASCADE;

-- Create schema for operational sources
CREATE SCHEMA sources;

-- 1. Sales Domain: CRM Customers
CREATE TABLE sources.crm_customers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    signup_date TIMESTAMP
);

INSERT INTO sources.crm_customers (id, first_name, last_name, email, signup_date) VALUES
(1, 'John', 'Doe', 'john.doe@example.com', '2024-01-15 10:30:00'),
(2, 'Jane', 'Smith', 'jane.smith@example.com', '2024-02-20 14:00:00'),
(3, 'Peter', 'Jones', 'peter.jones@example.com', '2024-03-10 09:00:00')
ON CONFLICT (id) DO NOTHING;

-- 2. Sales Domain: ERP Orders
CREATE TABLE sources.erp_orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES sources.crm_customers(id),
    order_date TIMESTAMP,
    total_amount DECIMAL(10, 2)
);

INSERT INTO sources.erp_orders (order_id, customer_id, order_date, total_amount) VALUES
(1, 1, '2024-05-01 11:00:00', 150.75),
(2, 1, '2024-05-15 16:20:00', 200.00),
(3, 2, '2024-05-02 08:45:00', 75.50),
(4, 3, '2024-05-20 12:00:00', 500.25),
(5, 2, '2024-06-01 18:00:00', 120.00)
ON CONFLICT (order_id) DO NOTHING;


-- 3. Logistics Domain: WMS Shipments
CREATE TABLE sources.wms_shipments (
    shipment_id SERIAL PRIMARY KEY,
    order_ref INTEGER REFERENCES sources.erp_orders(order_id),
    shipped_date TIMESTAMP,
    delivery_status VARCHAR(20)
);

INSERT INTO sources.wms_shipments (shipment_id, order_ref, shipped_date, delivery_status) VALUES
(1, 1, '2024-05-02 09:00:00', 'Delivered'),
(2, 2, '2024-05-16 10:00:00', 'In Transit'),
(3, 3, '2024-05-02 14:00:00', 'Delivered'),
(4, 4, '2024-05-21 15:30:00', 'Shipped')
ON CONFLICT (shipment_id) DO NOTHING;
-- Note: Order 5 has not been shipped yet to represent a realistic scenario.

-- Reset sequences to avoid conflicts if data is re-inserted manually
SELECT setval('sources.crm_customers_id_seq', (SELECT MAX(id) FROM sources.crm_customers));
SELECT setval('sources.erp_orders_order_id_seq', (SELECT MAX(order_id) FROM sources.erp_orders));
SELECT setval('sources.wms_shipments_shipment_id_seq', (SELECT MAX(shipment_id) FROM sources.wms_shipments));
