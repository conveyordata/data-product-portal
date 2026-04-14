-- Setup Schemas
CREATE SCHEMA IF NOT EXISTS inventory_snapshot;
CREATE SCHEMA IF NOT EXISTS sales_transaction_ledger;
CREATE SCHEMA IF NOT EXISTS customer_demographic_master;

-- ==========================================
-- INVENTORY SNAPSHOT DOMAIN
-- ==========================================

CREATE TABLE inventory_snapshot.inventory_latest (
    sku VARCHAR(50) PRIMARY KEY,
    qty_oh INT, -- Abbreviation: Quantity On Hand
    warehouse_id INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory_snapshot.stock_levels (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50),
    qty_oh INT,
    loc_id INT, -- Abbreviation: Location ID
    is_retired BOOLEAN DEFAULT FALSE, -- Implicit Filter
    captured_at TIMESTAMP
);

-- Populate Inventory Snapshot (More data points for trends and complexity)
INSERT INTO inventory_snapshot.inventory_latest (sku, qty_oh, warehouse_id) VALUES
('CAMP-TENT-4P', 12, 1),
('CAMP-STOVE-1', 45, 1),
('CAMP-CHAIR-LUXE', 20, 1),
('HIKE-BOOTS-M', 0, 2),
('HIKE-PACK-30L', 15, 2),
('CLIMB-ROPE-60M', 8, 1);

INSERT INTO inventory_snapshot.stock_levels (sku, qty_oh, loc_id, is_retired, captured_at) VALUES
('CAMP-TENT-4P', 15, 1, FALSE, '2026-01-01 10:00:00'),
('CAMP-TENT-4P', 14, 1, FALSE, '2026-01-15 10:00:00'),
('CAMP-TENT-4P', 12, 1, FALSE, '2026-02-01 10:00:00'),
('CAMP-STOVE-1', 50, 1, FALSE, '2026-01-01 10:00:00'),
('CAMP-STOVE-1', 48, 1, FALSE, '2026-01-15 10:00:00'),
('CAMP-STOVE-1', 45, 1, FALSE, '2026-02-01 10:00:00'),
('OLD-GEAR-99', 100, 1, TRUE, '2026-01-01 10:00:00'), -- Retired
('OLD-GEAR-99', 95, 1, TRUE, '2026-02-01 10:00:00'); -- Retired

-- ==========================================
-- SALES TRANSACTION LEDGER DOMAIN
-- ==========================================

CREATE TABLE sales_transaction_ledger.orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    total_amount INT, -- Unit: Cents
    calculated_total INT, -- Stale Metric: Red herring, slightly wrong values
    status VARCHAR(20), -- Status trap: 'DELIVERED', 'SHIPPED', 'CANCELLED', NULL (for processing)
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    shipped_at TIMESTAMP -- Timestamp Ambiguity
);

CREATE TABLE sales_transaction_ledger.order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES sales_transaction_ledger.orders(order_id),
    sku VARCHAR(50),
    quantity INT,
    price_cents INT
);

CREATE TABLE sales_transaction_ledger.recurring_revenue (
    subscription_id SERIAL PRIMARY KEY,
    customer_id INT,
    mrr INT, -- Monthly Recurring Revenue (Cents)
    arr INT, -- Annual Recurring Revenue (Cents)
    status VARCHAR(20),
    started_at DATE,
    ended_at DATE -- For churn calculations
);

-- Populate Sales Transaction Ledger
INSERT INTO sales_transaction_ledger.orders (order_id, customer_id, total_amount, calculated_total, status, created_at, updated_at, shipped_at) VALUES
(1001, 1, 15000, 15100, 'SHIPPED', '2026-01-15 14:00:00', '2026-01-16 09:00:00', NULL),
(1002, 2, 8550, 8650, 'DELIVERED', '2026-02-05 11:00:00', '2026-02-07 15:30:00', '2026-02-07 15:30:00'),
(1003, 1, 22000, 22100, 'DELIVERED', '2026-02-01 09:00:00', '2026-02-03 10:00:00', '2026-02-02 16:00:00'),
(1004, 3, 4500, 4600, NULL, '2026-02-08 14:00:00', '2026-02-08 14:00:00', NULL), -- Processing
(1005, 4, 12500, 12600, 'SHIPPED', '2026-02-07 10:00:00', '2026-02-08 09:00:00', NULL);

INSERT INTO sales_transaction_ledger.order_items (order_id, sku, quantity, price_cents) VALUES
(1001, 'CAMP-TENT-4P', 1, 12000),
(1001, 'CAMP-STOVE-1', 1, 3000),
(1002, 'HIKE-BOOTS-M', 1, 8550),
(1003, 'CAMP-CHAIR-LUXE', 2, 11000),
(1004, 'HIKE-PACK-30L', 1, 4500),
(1005, 'CLIMB-ROPE-60M', 1, 12500);

INSERT INTO sales_transaction_ledger.recurring_revenue (customer_id, mrr, arr, status, started_at, ended_at) VALUES
(1, 2900, 34800, 'ACTIVE', '2025-12-01', NULL),
(2, NULL, NULL, 'TRIAL', '2026-02-01', NULL), -- Partial Data
(3, 1500, 18000, 'CANCELED', '2025-06-01', '2026-01-20'),
(5, 5000, 60000, 'ACTIVE', '2026-01-10', NULL);

-- ==========================================
-- CUSTOMER DEMOGRAPHIC MASTER DOMAIN
-- ==========================================

CREATE TABLE customer_demographic_master.customers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100),
    full_name VARCHAR(100),
    acquired_by INT, -- References Internal Admin ID (Not in this DB)
    status VARCHAR(20) DEFAULT 'registered', -- Red Herring Status
    signup_date DATE
);

CREATE TABLE customer_demographic_master.web_sessions (
    session_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50), -- Anonymous UUID
    page_path VARCHAR(255),
    viewed_at TIMESTAMP
);

-- Populate Customer Demographic Master
INSERT INTO customer_demographic_master.customers (id, email, full_name, acquired_by, status, signup_date) VALUES
(1, 'alice@example.com', 'Alice Smith', 99, 'active', '2025-11-20'),
(2, 'bob@example.com', 'Bob Jones', 99, 'registered', '2026-02-01'),
(3, 'charlie@example.com', 'Charlie Brown', 101, 'active', '2025-05-15'),
(4, 'dana@example.com', 'Dana White', 99, 'prospect', '2026-01-10'),
(5, 'eve@example.com', 'Eve Black', 102, 'active', '2026-01-05');

INSERT INTO customer_demographic_master.web_sessions (user_id, page_path, viewed_at) VALUES
('sess-8821', '/home', '2026-02-08 09:00:00'),
('sess-8821', '/products/tents', '2026-02-08 09:05:00'),
('sess-1122', '/checkout', '2026-02-08 10:00:00'),
('sess-3344', '/home', '2026-02-08 11:00:00');
