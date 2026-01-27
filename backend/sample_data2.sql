do $$
declare
    -- DOMAINS
    sales_id uuid;
    marketing_id uuid;
    logistics_id uuid;

    -- DATA PRODUCT TYPES
    source_aligned_type_id uuid;
    aggregated_type_id uuid;
    consumer_aligned_type_id uuid;

    -- USERS
    alice_id uuid;
    bob_id uuid;
    jane_id uuid;
    john_id uuid;

    -- ROLES
    admin_role_id uuid;

    -- PLATFORMS
    postgresql_id uuid;
    postgresql_service_id uuid;

    -- DATA PRODUCTS
    sales_crm_customers_dp_id uuid;
    sales_erp_orders_dp_id uuid;
    logistics_wms_shipments_dp_id uuid;

    -- DATASETS
    sales_crm_customers_ds_id uuid;
    sales_erp_orders_ds_id uuid;
    logistics_wms_shipments_ds_id uuid;

    -- DATA OUTPUTS
    sales_crm_customers_do_id uuid;
    sales_erp_orders_do_id uuid;
    logistics_wms_shipments_do_id uuid;

    sales_crm_customers_do_config_id uuid;
    sales_erp_orders_do_config_id uuid;
    logistics_wms_shipments_do_config_id uuid;

    -- LIFECYLE
    draft uuid;
    ready uuid;

begin
    TRUNCATE TABLE public.data_products_datasets CASCADE;
    TRUNCATE TABLE public.datasets CASCADE;
    TRUNCATE TABLE public.data_products CASCADE;
    TRUNCATE TABLE public.data_product_types CASCADE;
    TRUNCATE TABLE public.domains CASCADE;
    TRUNCATE TABLE public.tags CASCADE;
    TRUNCATE TABLE public.roles CASCADE;
    TRUNCATE TABLE public.role_assignments_global CASCADE;
    TRUNCATE TABLE public.role_assignments_data_product CASCADE;
    TRUNCATE TABLE public.role_assignments_dataset CASCADE;
    TRUNCATE TABLE public.dataset_curated_queries CASCADE;
    TRUNCATE TABLE public.data_outputs_datasets CASCADE;
    TRUNCATE TABLE public.data_outputs CASCADE;
    TRUNCATE TABLE public.data_output_configurations CASCADE;
    TRUNCATE TABLE public.tags_data_outputs CASCADE;
    TRUNCATE TABLE public.tags_data_products CASCADE;
    TRUNCATE TABLE public.tags_datasets CASCADE;
    TRUNCATE TABLE public.dataset_query_stats_daily CASCADE;
    TRUNCATE TABLE public.data_product_lifecycles CASCADE;

    -- DATA PRODUCT LIFECYLCE
    INSERT INTO data_product_lifecycles (id, name, "value", color, is_default, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'Draft', 0, 'grey', true, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO draft;
    INSERT INTO data_product_lifecycles (id, name, "value", color, is_default, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'Ready', 1, 'green', false, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO ready;

    -- DOMAINS
    INSERT INTO public.domains (id, "name", description, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'Sales', 'Responsible for all activities related to sales, customer relationships, and order management.', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO sales_id;
    INSERT INTO public.domains (id, "name", description, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'Marketing', 'Focused on customer outreach, promotions, and analyzing customer behavior to drive sales.', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO marketing_id;
    INSERT INTO public.domains (id, "name", description, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'Logistics', 'Manages inventory, warehousing, and the entire order fulfillment and shipping process.', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO logistics_id;

    -- DATA PRODUCT TYPES
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'source aligned', 'Data product aligned with a source system', 'INGESTION', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO source_aligned_type_id;
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'aggregated', 'Data product that aggregates data from multiple sources', 'PROCESSING', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO aggregated_type_id;
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'consumer aligned', 'Data product aligned with the needs of a specific consumer', 'REPORTING', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO consumer_aligned_type_id;

    -- USERS
    INSERT INTO public.users (email, id, external_id, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('alice.baker@pharma.com', 'a02d3714-97e3-40d8-92b7-3b018fd1229f', 'alice.baker@pharma.com', 'Alice', 'Baker', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) ON CONFLICT (email) DO NOTHING returning id INTO alice_id;
    INSERT INTO public.users (email, id, external_id, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('bob.johnson@pharma.com', '35f2dd11-3119-4eb3-8f19-01b323131221', 'bob.johnson@pharma.com', 'Bob', 'Johnson', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) ON CONFLICT (email) DO NOTHING returning id INTO bob_id;
    INSERT INTO public.users (email, id, external_id, can_become_admin, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('jane.researcher@pharma.com', 'd9f3aae2-391e-46c1-aec6-a7ae1114a7da', 'jane.researcher@pharma.com', true, 'Jane', 'Researcher', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) ON CONFLICT (email) DO NOTHING returning id INTO jane_id;
    INSERT INTO public.users (email, id, external_id, can_become_admin, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('john.scientist@pharma.com', 'b72fca38-17ff-4259-a075-5aaa5973343c', 'john.scientist@pharma.com', true, 'John', 'Scientist', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) ON CONFLICT (email) DO NOTHING returning id INTO john_id;

    -- ROLES
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('f80c101c-345c-4d5b-9524-57c55bd12d2d', 'Everyone', 'global', 1, 'This is the role that is used as fallback for users that don''t have another role', ARRAY [102, 103, 104, 105], timezone('utc'::text, CURRENT_TIMESTAMP + INTERVAL '1 seconds'), NULL, NULL);
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('e43b6f7a-e776-49b2-9b51-117d8644d971', 'Owner', 'data_product', 2, 'The owner of a Data Product', ARRAY [301, 302, 304, 305, 306, 307, 308, 309, 310, 311, 313, 314, 315], timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('18e67286-92aa-449a-ba46-ac26eb0de21d', 'Solution Architect', 'data_product', 0, 'The Solution Architect for a Data Product', ARRAY [303, 309, 310, 311, 312, 313, 314], timezone('utc'::text, CURRENT_TIMESTAMP + INTERVAL '1 seconds'), NULL, NULL);
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('9ca3bfdd-2919-4190-a8bb-55e9ee7d70dd', 'Member', 'data_product', 0, 'A regular team member of a Data Product', ARRAY [313, 314, 315], timezone('utc'::text, CURRENT_TIMESTAMP + INTERVAL '2 seconds'), NULL, NULL);
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('9a9d7deb-14d9-4257-a986-7900aa70ef8f', 'Owner', 'dataset', 2, 'The owner of a Dataset', ARRAY [401, 402, 404, 405, 406, 407, 408, 411, 412, 413], timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('2ae1b4e3-5b13-491a-912b-984e2e90b858', 'Solution Architect', 'dataset', 0, 'The Solution Architect for a Dataset', ARRAY [403, 409, 410], timezone('utc'::text, CURRENT_TIMESTAMP + INTERVAL '1 seconds'), NULL, NULL);
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('db8d7a76-c50b-4e95-8549-8da86f48e7c2', 'Member', 'dataset', 0, 'A regular team member of a Dataset', ARRAY [413], timezone('utc'::text, CURRENT_TIMESTAMP + INTERVAL '2 seconds'), NULL, NULL);
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at)
    VALUES
        ('00000000-0000-0000-0000-000000000000', 'Admin', 'global', 3, 'Global admin role', ARRAY[]::integer[], timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL)
    RETURNING id INTO admin_role_id;

    -- PLATFORMS
    INSERT INTO public.platforms (id, "name") VALUES ('99898d61-ba3b-4f30-a929-8356ccfe521f', 'PostgreSQL') returning id INTO postgresql_id;
    INSERT INTO public.platform_services (id, "name", platform_id, result_string_template, technical_info_template) VALUES ('242d7e16-edd5-41e1-9e25-775ecc29706e', 'PostgreSQL', postgresql_id, '{database}.{schema}.{table}', '{database}.{schema}.{table}') returning id INTO postgresql_service_id;
    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('38c320c3-8b66-439f-abab-6b78d225ae27', postgresql_id, postgresql_service_id, '["dpp_demo"]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- GLOBAL ROLE ASSIGNMENTS
    -- Make john.scientist an admin
    INSERT into public.role_assignments_global (id, user_id, role_id, decision, requested_on, decided_on)
    SELECT gen_random_uuid(), id, admin_role_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP)
    FROM public.users WHERE email = 'john.scientist@pharma.com';

    -- DATA PRODUCTS
    INSERT INTO public.data_products (id, "name", namespace, description, about, status, type_id, domain_id, created_on, updated_on, deleted_at, lifecycle_id) VALUES (gen_random_uuid(), 'Sales CRM Customers', 'sales-crm-customers', 'Provides a clean, trusted view of customer account information, sourced directly from our CRM.', '<h3>Value Proposition</h3>
<p>This data product establishes a single source of truth for customer identities. By unifying fragmented CRM records, it enables consistent personalization, improved customer relationship management, and highly targeted marketing efforts across all business units.<br></p>

<h3>User Consumption Mode</h3>
<p><strong>Analytical & Operational:</strong> Optimized for both high-performance operational lookups and comprehensive historical trend analysis.<br></p>

<h3>Recommended Use Cases</h3>
<p><ul>
  <li><strong>Marketing:</strong> Segmentation for email campaigns and loyalty programs.</li>
  <li><strong>Support:</strong> Providing agents with a 360-degree view of customer history.</li>
  <li><strong>Data Science:</strong> Building churn prediction and lifetime value models.</li>
</ul></p>

<h3>Terms of Use</h3>
<p><strong>Usage:</strong> Approved for all internal analytics, marketing automation, and customer support workflows.</p>
<p><strong>Limitations:</strong> Not authorized for external regulatory reporting. Handing of PII must strictly adhere to the corporate GDPR compliance framework.</p>', 'ACTIVE', source_aligned_type_id, sales_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, ready) returning id INTO sales_crm_customers_dp_id;

    INSERT INTO public.data_products (id, "name", namespace, description, about, status, type_id, domain_id, created_on, updated_on, deleted_at, lifecycle_id) VALUES (gen_random_uuid(), 'Sales ERP Orders', 'sales-erp-orders', 'Provides real-time order data from our ERP system.', '<h3>Value Proposition</h3>
<p>Provides immediate visibility into sales transactions as they happen. This real-time feed empowers leadership with instant revenue recognition and allows supply chain teams to react quickly to shifting demand patterns.<br></p>

<h3>User Consumption Mode</h3>
<p><strong>Operational & Streaming:</strong> Designed for near real-time monitoring and triggering automated downstream fulfillment workflows.<br></p>

<h3>Recommended Use Cases</h3>
<p><ul>
  <li><strong>Finance:</strong> Real-time revenue tracking and daily sales performance monitoring.</li>
  <li><strong>Operations:</strong> Identifying and prioritizing urgent order fulfillment.</li>
  <li><strong>Sales:</strong> Automated calculation of daily sales commissions.</li>
</ul></p>

<h3>Terms of Use</h3>
<p><strong>Usage:</strong> Approved for internal financial planning, operational monitoring, and sales performance tracking.</p>
<p><strong>Limitations:</strong> This is a real-time feed and may include pending transactions. It is not the master record for audited financial statements. Historical corrections can occur within a 24-hour window.</p>', 'ACTIVE', source_aligned_type_id, sales_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, ready) returning id INTO sales_erp_orders_dp_id;

    INSERT INTO public.data_products (id, "name", namespace, description, about, status, type_id, domain_id, created_on, updated_on, deleted_at, lifecycle_id) VALUES (gen_random_uuid(), 'Logistics WMS Shipments', 'logistics-wms-shipments', 'Tracks order shipment and delivery status from the warehouse.', '<h3>Value Proposition</h3>
<p>Optimizes the "last mile" of the supply chain by providing granular, end-to-end tracking of every package. It reduces operational overhead by automating status updates and proactively identifying potential delivery delays.<br></p>

<h3>User Consumption Mode</h3>
<p><strong>Operational:</strong> Refreshed hourly to support active logistics coordination and customer-facing notification systems.<br></p>

<h3>Recommended Use Cases</h3>
<p><ul>
  <li><strong>Customer Experience:</strong> Powering real-time delivery estimation updates for customers.</li>
  <li><strong>Logistics:</strong> Evaluating carrier performance and reliability metrics.</li>
  <li><strong>Security:</strong> Rapid investigation and resolution of lost or delayed package claims.</li>
</ul></p>

<h3>Terms of Use</h3>
<p><strong>Usage:</strong> Approved for logistics optimization, carrier management, and customer service inquiry resolution.</p>
<p><strong>Limitations:</strong> Data accuracy is dependent on third-party carrier scan events. Not suitable as sole evidence in legal delivery disputes without secondary carrier documentation.</p>', 'ACTIVE', source_aligned_type_id, logistics_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, ready) returning id INTO logistics_wms_shipments_dp_id;

    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_crm_customers_dp_id, john_id, 'e43b6f7a-e776-49b2-9b51-117d8644d971', 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_erp_orders_dp_id, john_id, 'e43b6f7a-e776-49b2-9b51-117d8644d971', 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), logistics_wms_shipments_dp_id, john_id, 'e43b6f7a-e776-49b2-9b51-117d8644d971', 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- DATA OUTPUT CONFIGURATIONS
    INSERT INTO public.data_output_configurations (id, configuration_type, "database", "schema", "table", database_path, table_path, bucket_identifier) VALUES (gen_random_uuid(), 'PostgreSQLDataOutput', 'dpp_demo', 'sales_crm_customers', '*', 'dpp_demo', '*', '') returning id INTO sales_crm_customers_do_config_id;
    INSERT INTO public.data_output_configurations (id, configuration_type, "database", "schema", "table", database_path, table_path, bucket_identifier) VALUES (gen_random_uuid(), 'PostgreSQLDataOutput', 'dpp_demo', 'sales_erp_orders', '*', 'dpp_demo', '*', '') returning id INTO sales_erp_orders_do_config_id;
    INSERT INTO public.data_output_configurations (id, configuration_type, "database", "schema", "table", database_path, table_path, bucket_identifier) VALUES (gen_random_uuid(), 'PostgreSQLDataOutput', 'dpp_demo', 'logistics_wms_shipments', '*', 'dpp_demo', '*', '') returning id INTO logistics_wms_shipments_do_config_id;

    -- DATA OUTPUTS
    INSERT INTO public.data_outputs (id, configuration_id, "name", namespace, description, status, owner_id, platform_id, service_id, created_on, updated_on, deleted_at, "sourceAligned") VALUES (gen_random_uuid(), sales_crm_customers_do_config_id, 'Sales CRM Customers', 'sales-crm-customers', 'Customer account information', 'ACTIVE', sales_crm_customers_dp_id, postgresql_id, postgresql_service_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, true) returning id INTO sales_crm_customers_do_id;
    INSERT INTO public.data_outputs (id, configuration_id, "name", namespace, description, status, owner_id, platform_id, service_id, created_on, updated_on, deleted_at, "sourceAligned") VALUES (gen_random_uuid(), sales_erp_orders_do_config_id, 'Sales ERP Orders', 'sales-erp-orders', 'Order data', 'ACTIVE', sales_erp_orders_dp_id, postgresql_id, postgresql_service_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, true) returning id INTO sales_erp_orders_do_id;
    INSERT INTO public.data_outputs (id, configuration_id, "name", namespace, description, status, owner_id, platform_id, service_id, created_on, updated_on, deleted_at, "sourceAligned") VALUES (gen_random_uuid(), logistics_wms_shipments_do_config_id, 'Logistics WMS Shipments', 'logistics-wms-shipments', 'Shipment and delivery status', 'ACTIVE', logistics_wms_shipments_dp_id, postgresql_id, postgresql_service_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, true) returning id INTO logistics_wms_shipments_do_id;

    -- DATASETS
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, domain_id, created_on, updated_on, deleted_at, lifecycle_id) VALUES (gen_random_uuid(), 'customers', sales_crm_customers_dp_id, 'Customers', 'Customer account information from the CRM', '<p><strong>Version:</strong> 1.0.0 &nbsp;|&nbsp; <strong>Freshness:</strong> Daily (Morning sync)</p><p>This dataset contains curated customer information from the Sales CRM, providing a single source of truth for customer identity and contact details.</p><br><h3>How to Use</h3><p>Use this dataset to enrich sales data with customer demographic information or for marketing campaign targeting. Join with the <code>Orders</code> dataset on <code>customer_id</code>.</p><br><h3>Table Schema</h3><table><thead><tr><th>Column Name</th><th>Type</th><th>Description</th></tr></thead><tbody><tr><td>id</td><td>Integer</td><td>Unique identifier for the customer.</td></tr><tr><td>first_name</td><td>String</td><td>Customer''s first name.</td></tr><tr><td>last_name</td><td>String</td><td>Customer''s last name.</td></tr><tr><td>email</td><td>String</td><td>Primary contact email address.</td></tr><tr><td>signup_date</td><td>Timestamp</td><td>Timestamp when the customer registered.</td></tr></tbody></table>', 'ACTIVE', 'RESTRICTED', sales_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, ready) returning id INTO sales_crm_customers_ds_id;
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, domain_id, created_on, updated_on, deleted_at, lifecycle_id) VALUES (gen_random_uuid(), 'orders', sales_erp_orders_dp_id, 'Orders', 'Order data from the ERP system', '<p><strong>Version:</strong> 1.1.0 &nbsp;|&nbsp; <strong>Freshness:</strong> Real-time (near real-time via ERP hooks)</p><p>Provides detailed transaction history for all sales orders processed through the ERP system.</p><br><h3>How to Use</h3><p>This dataset is the primary source for revenue analysis and order volume tracking. It can be joined with <code>Customers</code> for customer-level insights or <code>Shipments</code> for fulfillment tracking.</p><br><h3>Table Schema</h3><table><thead><tr><th>Column Name</th><th>Type</th><th>Description</th></tr></thead><tbody><tr><td>order_id</td><td>Integer</td><td>Unique identifier for the order.</td></tr><tr><td>customer_id</td><td>Integer</td><td>Reference to the customer who placed the order.</td></tr><tr><td>order_date</td><td>Timestamp</td><td>Timestamp of order placement.</td></tr><tr><td>total_amount</td><td>Decimal</td><td>Total monetary value of the order.</td></tr></tbody></table>', 'ACTIVE', 'RESTRICTED', sales_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, ready) returning id INTO sales_erp_orders_ds_id;
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, domain_id, created_on, updated_on, deleted_at, lifecycle_id) VALUES (gen_random_uuid(), 'shipments', logistics_wms_shipments_dp_id, 'Shipments', 'Shipment and delivery status from the WMS', '<p><strong>Version:</strong> 1.0.2 &nbsp;|&nbsp; <strong>Freshness:</strong> Hourly updates</p><p>Tracks the fulfillment lifecycle of orders, from warehouse dispatch to final delivery status.</p><br><h3>How to Use</h3><p>Utilize this data to monitor delivery times, identify shipping bottlenecks, and calculate order fulfillment rates. Join with <code>Orders</code> on <code>order_ref</code>.</p><br><h3>Table Schema</h3><table><thead><tr><th>Column Name</th><th>Type</th><th>Description</th></tr></thead><tbody><tr><td>shipment_id</td><td>Integer</td><td>Unique identifier for the shipment record.</td></tr><tr><td>order_ref</td><td>Integer</td><td>Reference to the corresponding ERP order.</td></tr><tr><td>shipped_date</td><td>Timestamp</td><td>Timestamp when the package left the warehouse.</td></tr><tr><td>delivery_status</td><td>String</td><td>Current status of the delivery (e.g., Shipped, In Transit, Delivered).</td></tr></tbody></table>', 'ACTIVE', 'RESTRICTED', logistics_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, ready) returning id INTO logistics_wms_shipments_ds_id;

    INSERT INTO public.role_assignments_dataset (id, dataset_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_crm_customers_ds_id, john_id, '9a9d7deb-14d9-4257-a986-7900aa70ef8f', 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.role_assignments_dataset (id, dataset_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_erp_orders_ds_id, john_id, '9a9d7deb-14d9-4257-a986-7900aa70ef8f', 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.role_assignments_dataset (id, dataset_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), logistics_wms_shipments_ds_id, john_id, '9a9d7deb-14d9-4257-a986-7900aa70ef8f', 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- DATA OUTPUTS - DATASETS
    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_crm_customers_do_id, sales_crm_customers_ds_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_erp_orders_do_id, sales_erp_orders_ds_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), logistics_wms_shipments_do_id, logistics_wms_shipments_ds_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- ------------------------------------------------------------------------------------------------
    -- START of Insert dynamic dataset query stats
    -- ------------------------------------------------------------------------------------------------

    -- Sales CRM Customers usage
    INSERT INTO public.dataset_query_stats_daily (date, dataset_id, consumer_data_product_id, query_count)
    SELECT gs::date, sales_crm_customers_ds_id, sales_erp_orders_dp_id, 15
    FROM generate_series((CURRENT_DATE - INTERVAL '3 months')::date, CURRENT_DATE - 1, INTERVAL '1 day') AS gs
    WHERE EXTRACT(ISODOW FROM gs) BETWEEN 1 AND 5;

    -- Sales ERP Orders usage
    INSERT INTO public.dataset_query_stats_daily (date, dataset_id, consumer_data_product_id, query_count)
    SELECT gs::date, sales_erp_orders_ds_id, logistics_wms_shipments_dp_id, 8
    FROM generate_series((CURRENT_DATE - INTERVAL '3 months')::date, CURRENT_DATE - 1, INTERVAL '1 day') AS gs;

    -- Logistics WMS Shipments usage
    INSERT INTO public.dataset_query_stats_daily (date, dataset_id, consumer_data_product_id, query_count)
    SELECT gs::date, logistics_wms_shipments_ds_id, sales_crm_customers_dp_id, 5
    FROM generate_series((CURRENT_DATE - INTERVAL '3 months')::date, CURRENT_DATE - 1, INTERVAL '1 day') AS gs
    WHERE EXTRACT(ISODOW FROM gs) = 1;

    -- ------------------------------------------------------------------------------------------------
    -- END of Insert dynamic dataset query stats
    -- ------------------------------------------------------------------------------------------------

    -- DATASET CURATED QUERIES
    INSERT INTO public.dataset_curated_queries (output_port_id, title, description, query_text, sort_order)
    VALUES (
        sales_crm_customers_ds_id,
        'Active Customers',
        'Retrieve a list of active customers with their contact details.',
        'SELECT customer_id, name, email, phone
         FROM customers
         WHERE status = ''ACTIVE''
         ORDER BY name ASC;',
        0
    );

end $$;
