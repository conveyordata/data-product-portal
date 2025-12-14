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
    INSERT INTO data_product_lifecycles (id, name, "value", color, is_default, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'Draft', 0, 'grey', true, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO data_product_lifecycles (id, name, "value", color, is_default, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'Ready', 1, 'green', false, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

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
    INSERT INTO public.platforms (id, "name") VALUES ('99898d61-ba3b-4f30-a929-8356ccfe521f', 'PostgreSQL') ON CONFLICT (id) DO NOTHING;
    SELECT id into postgresql_id from public.platforms where name = 'PostgreSQL';

    INSERT INTO public.platform_services (id, "name", platform_id, result_string_template, technical_info_template) VALUES ('242d7e16-edd5-41e1-9e25-775ecc29706e', 'PostgreSQL', postgresql_id, '{database}.{schema}.{table}', '{database}.{schema}.{table}') ON CONFLICT (id) DO NOTHING;
    SELECT id into postgresql_service_id from public.platform_services where name = 'PostgreSQL';

    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('38c320c3-8b66-439f-abab-6b78d225ae27', postgresql_id, postgresql_service_id, '["sources", "products"]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) ON CONFLICT(id) DO NOTHING;

    -- GLOBAL ROLE ASSIGNMENTS
    -- Make john.scientist an admin
    INSERT into public.role_assignments_global (id, user_id, role_id, decision, requested_on, decided_on)
    SELECT gen_random_uuid(), id, admin_role_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP)
    FROM public.users WHERE email = 'john.scientist@pharma.com';

    -- -- DATA PRODUCTS
    -- INSERT INTO public.data_products (id, "name", namespace, description, about, status, type_id, domain_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'Sales CRM Customers', 'sales-crm-customers', 'Provides a clean, trusted view of customer account information, sourced directly from our CRM.', 'about', 'ACTIVE', source_aligned_type_id, sales_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO sales_crm_customers_dp_id;
    -- INSERT INTO public.data_products (id, "name", namespace, description, about, status, type_id, domain_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'Sales ERP Orders', 'sales-erp-orders', 'Provides real-time order data from our ERP system.', 'about', 'ACTIVE', source_aligned_type_id, sales_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO sales_erp_orders_dp_id;
    -- INSERT INTO public.data_products (id, "name", namespace, description, about, status, type_id, domain_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'Logistics WMS Shipments', 'logistics-wms-shipments', 'Tracks order shipment and delivery status from the warehouse.', 'about', 'ACTIVE', source_aligned_type_id, logistics_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO logistics_wms_shipments_dp_id;

    -- -- DATASETS
    -- INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, domain_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'customers', sales_crm_customers_dp_id, 'Customers', 'Customer account information from the CRM', 'about', 'ACTIVE', 'PUBLIC', sales_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO sales_crm_customers_ds_id;
    -- INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, domain_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'orders', sales_erp_orders_dp_id, 'Orders', 'Order data from the ERP system', 'about', 'ACTIVE', 'PUBLIC', sales_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO sales_erp_orders_ds_id;
    -- INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, domain_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'shipments', logistics_wms_shipments_dp_id, 'Shipments', 'Shipment and delivery status from the WMS', 'about', 'ACTIVE', 'PUBLIC', logistics_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO logistics_wms_shipments_ds_id;

    -- -- DATA OUTPUT CONFIGURATIONS
    -- INSERT INTO public.data_output_configurations (id, configuration_type, "database", "schema", "table", database_path, table_path, bucket_identifier) VALUES (gen_random_uuid(), 'PostgreSQLDataOutput', 'products', 'sales_crm_customers', 'customers', '', '', '') returning id INTO sales_crm_customers_do_config_id;
    -- INSERT INTO public.data_output_configurations (id, configuration_type, "database", "schema", "table", database_path, table_path, bucket_identifier) VALUES (gen_random_uuid(), 'PostgreSQLDataOutput', 'products', 'sales_erp_orders', 'orders', '', '', '') returning id INTO sales_erp_orders_do_config_id;
    -- INSERT INTO public.data_output_configurations (id, configuration_type, "database", "schema", "table", database_path, table_path, bucket_identifier) VALUES (gen_random_uuid(), 'PostgreSQLDataOutput', 'products', 'logistics_wms_shipments', 'shipments', '', '', '') returning id INTO logistics_wms_shipments_do_config_id;

    -- -- DATA OUTPUTS
    -- INSERT INTO public.data_outputs (id, configuration_id, "name", namespace, description, status, owner_id, platform_id, service_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_crm_customers_do_config_id, 'Sales CRM Customers', 'sales-crm-customers', 'Customer account information', 'ACTIVE', sales_crm_customers_dp_id, postgresql_id, postgresql_service_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO sales_crm_customers_do_id;
    -- INSERT INTO public.data_outputs (id, configuration_id, "name", namespace, description, status, owner_id, platform_id, service_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_erp_orders_do_config_id, 'Sales ERP Orders', 'sales-erp-orders', 'Order data', 'ACTIVE', sales_erp_orders_dp_id, postgresql_id, postgresql_service_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO sales_erp_orders_do_id;
    -- INSERT INTO public.data_outputs (id, configuration_id, "name", namespace, description, status, owner_id, platform_id, service_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), logistics_wms_shipments_do_config_id, 'Logistics WMS Shipments', 'logistics-wms-shipments', 'Shipment and delivery status', 'ACTIVE', logistics_wms_shipments_dp_id, postgresql_id, postgresql_service_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO logistics_wms_shipments_do_id;

    -- DATA OUTPUTS - DATASETS
    -- INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status) VALUES (gen_random_uuid(), sales_crm_customers_do_id, sales_crm_customers_ds_id, 'APPROVED');
    -- INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status) VALUES (gen_random_uuid(), sales_erp_orders_do_id, sales_erp_orders_ds_id, 'APPROVED');
    -- INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status) VALUES (gen_random_uuid(), logistics_wms_shipments_do_id, logistics_wms_shipments_ds_id, 'APPROVED');

end $$;
