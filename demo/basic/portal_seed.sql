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
    sarah_id uuid;
    david_id uuid;
    mike_id uuid;
    emma_id uuid;

    -- ROLES
    admin_role_id uuid;

    -- PLATFORMS
    postgresql_id uuid;
    postgresql_service_id uuid;
    environment_id_dev uuid;
    aws_id uuid;
    s3_service_id uuid;
    glue_service_id uuid;
    semantic_model_id uuid;
    osi_sem_model_service_id uuid;

    -- DATA PRODUCTS
    sales_crm_customers_dp_id uuid;
    sales_erp_orders_dp_id uuid;
    logistics_wms_shipments_dp_id uuid;
    marketing_customer_360_dp_id uuid;
    campaign_activation_dp_id uuid;
    churn_model_dp_id uuid;

    -- DATASETS
    sales_crm_customers_ds_id uuid;
    sales_erp_orders_ds_id uuid;
    logistics_wms_shipments_ds_id uuid;
    marketing_customer_360_ds_id uuid;
    campaign_activation_ds_id uuid;
    churn_model_ds_id uuid;

    -- DATA OUTPUTS
    sales_crm_customers_do_id uuid;
    sales_erp_orders_do_id uuid;
    logistics_wms_shipments_do_id uuid;
    marketing_customer_360_do_id uuid;
    campaign_activation_do_id uuid;
    churn_model_do_id uuid;

    sales_crm_customers_do_config_id uuid;
    sales_erp_orders_do_config_id uuid;
    logistics_wms_shipments_do_config_id uuid;
    marketing_customer_360_do_config_id uuid;
    campaign_activation_do_config_id uuid;
    churn_model_do_config_id uuid;

    -- LIFECYLE
    draft uuid;
    ready uuid;

    -- DATA QUALITY SUMMARIES
    sales_crm_customers_dq_id uuid;
    sales_erp_orders_dq_id uuid;
    logistics_wms_shipments_dq_id uuid;
    marketing_customer_360_dq_id uuid;
    campaign_activation_dq_id uuid;
    churn_model_dq_id uuid;

begin
    TRUNCATE TABLE public.input_ports CASCADE;
    TRUNCATE TABLE public.datasets CASCADE;
    TRUNCATE TABLE public.abstract_data_products CASCADE;
    TRUNCATE TABLE public.data_product_types CASCADE;
    TRUNCATE TABLE public.domains CASCADE;
    TRUNCATE TABLE public.tags CASCADE;
    INSERT INTO public.tags (id, value) VALUES (gen_random_uuid(), 'PII');
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
    TRUNCATE TABLE public.output_port_cost_records CASCADE;
    TRUNCATE TABLE public.output_port_freshness_slos CASCADE;
    TRUNCATE TABLE public.output_port_freshness_observations CASCADE;
    TRUNCATE TABLE public.data_product_lifecycles CASCADE;
    TRUNCATE TABLE public.output_port_data_quality_summaries CASCADE;
    TRUNCATE TABLE public.data_quality_technical_assets CASCADE;

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
    INSERT INTO public.users (email, id, external_id, can_become_admin, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('alice.baker@pharma.com', 'a02d3714-97e3-40d8-92b7-3b018fd1229f', 'alice.baker@pharma.com', true, 'Alice', 'Baker', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) ON CONFLICT (email) DO NOTHING returning id INTO alice_id;
    INSERT INTO public.users (email, id, external_id, can_become_admin, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('bob.johnson@pharma.com', '35f2dd11-3119-4eb3-8f19-01b323131221', 'bob.johnson@pharma.com', true, 'Bob', 'Johnson', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) ON CONFLICT (email) DO NOTHING returning id INTO bob_id;
    INSERT INTO public.users (email, id, external_id, can_become_admin, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('jane.researcher@pharma.com', 'd9f3aae2-391e-46c1-aec6-a7ae1114a7da', 'jane.researcher@pharma.com', true, 'Jane', 'Researcher', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) ON CONFLICT (email) DO NOTHING returning id INTO jane_id;
    INSERT INTO public.users (email, id, external_id, can_become_admin, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('john.scientist@pharma.com', 'b72fca38-17ff-4259-a075-5aaa5973343c', 'john.scientist@pharma.com', true, 'John', 'Scientist', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) ON CONFLICT (email) DO NOTHING returning id INTO john_id;

    INSERT INTO public.users (email, id, external_id, can_become_admin, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('sarah.chen@pharma.com', 'f1a2b3c4-d5e6-7890-abcd-ef1234567801', 'sarah.chen@pharma.com', true, 'Sarah', 'Chen', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) ON CONFLICT (email) DO NOTHING returning id INTO sarah_id;
    INSERT INTO public.users (email, id, external_id, can_become_admin, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('david.miller@pharma.com', 'f1a2b3c4-d5e6-7890-abcd-ef1234567802', 'david.miller@pharma.com', true, 'David', 'Miller', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) ON CONFLICT (email) DO NOTHING returning id INTO david_id;
    INSERT INTO public.users (email, id, external_id, can_become_admin, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('mike.taylor@pharma.com', 'f1a2b3c4-d5e6-7890-abcd-ef1234567803', 'mike.taylor@pharma.com', true, 'Mike', 'Taylor', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) ON CONFLICT (email) DO NOTHING returning id INTO mike_id;
    INSERT INTO public.users (email, id, external_id, can_become_admin, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('emma.wilson@pharma.com', 'f1a2b3c4-d5e6-7890-abcd-ef1234567804', 'emma.wilson@pharma.com', true, 'Emma', 'Wilson', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) ON CONFLICT (email) DO NOTHING returning id INTO emma_id;

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

    INSERT INTO public.platforms (id, "name") VALUES (gen_random_uuid(), 'OSI') returning id INTO semantic_model_id;
    INSERT INTO public.platform_services (id, "name", platform_id, result_string_template, technical_info_template) VALUES (gen_random_uuid(), 'OSI', semantic_model_id, '{model_name}', '{file_path}') returning id INTO osi_sem_model_service_id;
    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), semantic_model_id, osi_sem_model_service_id, '[]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    SELECT id FROM public.platforms WHERE name = 'AWS' INTO aws_id;
    SELECT id FROM public.platform_services WHERE platform_id = aws_id AND name = 'S3' INTO s3_service_id;
    SELECT id FROM public.platform_services WHERE platform_id = aws_id AND name = 'Glue' INTO glue_service_id;
    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('6bd82fd6-9a23-4517-a07c-9110d83ab38f', aws_id, s3_service_id, '["datalake","ingress","egress"]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('fa026b3a-7a17-4c32-b279-995af021f6c2', aws_id, glue_service_id, '["clean","master"]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- ENVIRONMENTS
    INSERT INTO public.environments ("name", context, acronym, is_default, created_on, updated_on, deleted_at) VALUES ('development', '', 'dev', true, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO environment_id_dev;
    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES ('daa8e3e8-1485-4eb2-8b4b-575e8d10a570', environment_id_dev, postgresql_id, postgresql_service_id, '[{"identifier":"database", "host": "data-product-portal-postgresql-demo", "port": "5432", "admin_user": "postgres", "admin_pwd": "abc123"}]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- GLOBAL ROLE ASSIGNMENTS
    -- Make john.scientist an admin
    INSERT into public.role_assignments_global (id, user_id, role_id, decision, requested_on, decided_on)
    SELECT gen_random_uuid(), id, admin_role_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP)
    FROM public.users WHERE email = 'john.scientist@pharma.com';

    -- DATA PRODUCTS
    sales_crm_customers_dp_id    := '11111111-0000-0000-0000-000000000001'::uuid;
    sales_erp_orders_dp_id       := '11111111-0000-0000-0000-000000000002'::uuid;
    logistics_wms_shipments_dp_id := '11111111-0000-0000-0000-000000000003'::uuid;
    marketing_customer_360_dp_id  := '11111111-0000-0000-0000-000000000004'::uuid;
    campaign_activation_dp_id     := '11111111-0000-0000-0000-000000000005'::uuid;
    churn_model_dp_id             := '11111111-0000-0000-0000-000000000006'::uuid;

    INSERT INTO public.abstract_data_products (id, "name", namespace, description, domain_id, abstract_data_product_type, created_on, updated_on, deleted_at) VALUES (sales_crm_customers_dp_id, 'Sales CRM Customers', 'sales-crm-customers', 'Provides a clean, trusted view of customer account information, sourced directly from our CRM.', sales_id, 'data_products', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products (id, about, status, type_id, lifecycle_id) VALUES (sales_crm_customers_dp_id, '<h3>Value Proposition</h3><p>This data product establishes a single source of truth for customer identities. By unifying fragmented CRM records, it enables consistent personalization, improved customer relationship management, and highly targeted marketing efforts across all business units.<br></p><h3>User Consumption Mode</h3><p><strong>Analytical & Operational:</strong> Optimized for both high-performance operational lookups and comprehensive historical trend analysis.<br></p><h3>Recommended Use Cases</h3><ul><li><p><strong>Marketing:</strong> Segmentation for email campaigns and loyalty programs.</p></li><li><p><strong>Support:</strong> Providing agents with a 360-degree view of customer history.</p></li><li><p><strong>Data Science:</strong> Building churn prediction and lifetime value models.</p></li></ul><p></p><h3>Business Entities</h3><ul><li><p><strong>Customer:</strong> A person who has an active or historical relationship with the company. Includes identity information (name, email), account status, and registration history. This is the canonical record of who our customers are — every other domain references back to this identity.</p></li></ul><p></p><h3>Business Process</h3><p>Account managers and the inside sales team maintain and update customer records in the CRM throughout the sales cycle — from initial prospect qualification through contract signing and ongoing account management. This data product reflects the current state of those records, cleansed of duplicates and enriched with standardized contact details, so that every team works from the same authoritative customer identity.<br></p><h3>Legal Basis</h3><p>Contract (GDPR Art. 6(1)(b))<br></p><h3>Limitations</h3><p>Not authorized for external regulatory reporting. Handling of PII must strictly adhere to the corporate GDPR compliance framework.<br></p>', 'ACTIVE', source_aligned_type_id, ready);

    INSERT INTO public.abstract_data_products (id, "name", namespace, description, domain_id, abstract_data_product_type, created_on, updated_on, deleted_at) VALUES (sales_erp_orders_dp_id, 'Sales ERP Orders', 'sales-erp-orders', 'Provides real-time order data from our ERP system.', sales_id, 'data_products', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products (id, about, status, type_id, lifecycle_id) VALUES (sales_erp_orders_dp_id, '<h3>Value Proposition</h3><p>Provides immediate visibility into sales transactions as they happen. This real-time feed empowers leadership with instant revenue recognition and allows supply chain teams to react quickly to shifting demand patterns.<br></p><h3>User Consumption Mode</h3><p><strong>Operational & Streaming:</strong> Designed for near real-time monitoring and triggering automated downstream fulfillment workflows.<br></p><h3>Recommended Use Cases</h3><ul><li><p><strong>Finance:</strong> Real-time revenue tracking and daily sales performance monitoring.</p></li><li><p><strong>Operations:</strong> Identifying and prioritizing urgent order fulfillment.</p></li><li><p><strong>Sales:</strong> Automated calculation of daily sales commissions.</p></li></ul><p></p><h3>Business Entities</h3><ul><li><p><strong>Order:</strong> A confirmed commercial transaction between a customer and the company. Captures what was ordered, at what price, and when — the financial commitment that drives revenue recognition.</p></li><li><p><strong>Order Line:</strong> An individual line item within an order, representing a specific product or SKU with its quantity and unit price. Multiple order lines combine to form a complete order.</p></li></ul><p></p><h3>Business Process</h3><p>When a sales representative closes a deal or a customer submits a web order, the transaction is recorded in the ERP. The order moves through several states — draft, confirmed, fulfilled, invoiced — as the finance and operations teams process it. This data product exposes the full lifecycle of every order in near real-time, giving finance visibility for revenue recognition and operations a signal for fulfillment prioritisation.<br></p><h3>Legal Basis</h3><p>Contract (GDPR Art. 6(1)(b))<br></p><h3>Limitations</h3><p>This is a real-time feed and may include pending transactions. It is not the master record for audited financial statements. Historical corrections can occur within a 24-hour window.<br></p>', 'ACTIVE', source_aligned_type_id, ready);

    INSERT INTO public.abstract_data_products (id, "name", namespace, description, domain_id, abstract_data_product_type, created_on, updated_on, deleted_at) VALUES (logistics_wms_shipments_dp_id, 'Logistics WMS Shipments', 'logistics-wms-shipments', 'Tracks order shipment and delivery status from the warehouse.', logistics_id, 'data_products', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products (id, about, status, type_id, lifecycle_id) VALUES (logistics_wms_shipments_dp_id, '<h3>Value Proposition</h3><p>Optimizes the "last mile" of the supply chain by providing granular, end-to-end tracking of every package. It reduces operational overhead by automating status updates and proactively identifying potential delivery delays.<br></p><h3>User Consumption Mode</h3><p><strong>Operational:</strong> Refreshed hourly to support active logistics coordination and customer-facing notification systems.<br></p><h3>Recommended Use Cases</h3><ul><li><p><strong>Customer Experience:</strong> Powering real-time delivery estimation updates for customers.</p></li><li><p><strong>Logistics:</strong> Evaluating carrier performance and reliability metrics.</p></li><li><p><strong>Security:</strong> Rapid investigation and resolution of lost or delayed package claims.</p></li></ul><p></p><h3>Business Entities</h3><p><strong>Shipment:</strong> A physical dispatch of goods associated with a customer order. Tracks the journey of a package from warehouse pick-and-pack through carrier handoff to final delivery confirmation.<br><strong>Carrier:</strong> The third-party logistics provider responsible for transporting the shipment (e.g. DHL, FedEx). Carrier performance data is derived from scan events logged at each transit milestone.<br></p><h3>Business Process</h3><p>Once an order is confirmed in the ERP, the warehouse team picks, packs, and dispatches the goods. Each handoff — from warehouse to carrier, from carrier hub to local depot, and from depot to customer doorstep — generates a scan event that flows into the WMS. The customer service team uses this data to answer delivery queries, and the logistics team uses it to measure carrier reliability and SLA compliance.<br></p><h3>Intended Use</h3><p>Approved for logistics optimization, carrier management, and customer service inquiry resolution.<br></p><h3>Legal Basis</h3><p>Legitimate Interest (GDPR Art. 6(1)(f))<br></p><h3>Limitations</h3><p>Data accuracy is dependent on third-party carrier scan events. Not suitable as sole evidence in legal delivery disputes without secondary carrier documentation.<br></p>', 'ACTIVE', source_aligned_type_id, ready);

    INSERT INTO public.abstract_data_products (id, "name", namespace, description, domain_id, abstract_data_product_type, created_on, updated_on, deleted_at) VALUES (marketing_customer_360_dp_id, 'Marketing Customer 360', 'marketing-customer-360', 'A consolidated view of customer activity, combining customer profiles, order history, and shipment status for marketing analysis.', marketing_id, 'data_products', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products (id, about, status, type_id, lifecycle_id) VALUES (marketing_customer_360_dp_id, '<h3>Value Proposition</h3><p>This data product consolidates fragmented customer signals into a single, authoritative view. By unifying CRM profiles with transactional order history and real-time shipment status, it empowers marketing, data science, and support teams to execute with precision and build lasting customer relationships.<br></p><h3>User Consumption Mode</h3><p><strong>Analytical & Operational:</strong> Optimized for both high-performance operational lookups and comprehensive historical trend analysis.</p><p></p><h3>Recommended Use Cases</h3><ul><li><p><strong>Marketing:</strong> Segmentation for email campaigns and loyalty programs.</p></li><li><p><strong>Support:</strong> Providing agents with a 360-degree view of customer history.</p></li><li><p><strong>Data Science:</strong> Building churn prediction and lifetime value models.</p></li></ul><p></p><h3>Business Entities</h3><ul><li><p><strong>Customer:</strong> The individual whose full commercial relationship with the company is represented here — combining who they are (from CRM), what they have bought (from ERP), and how their orders were fulfilled (from Logistics).</p></li><li><p><strong>Order:</strong> The purchase history that tells us how valuable and loyal a customer is — total spend, order frequency, and recency.</p></li><li><p><strong>Shipment:</strong> Fulfilment experience data that influences customer satisfaction and churn risk — whether orders arrived on time and in good condition.</p></li><li><p><strong>Audience Segment:</strong> The derived RFM classification (e.g. Champions, At Risk, Churned) that groups customers by behavioural pattern for targeted marketing activation.</p></li></ul><p></p><h3>Business Process</h3><p>The Marketing Analytics team assembles this 360-degree view by joining the daily CRM refresh with the ERP order history and the latest WMS shipment status. The result is a single, consent-governed record per customer that the marketing team uses to plan campaigns, the data science team uses to train predictive models, and customer support uses to understand a customer''s recent journey before reaching out.<br></p><h3>Intended Use</h3><p>Audience segmentation for marketing campaigns; consent-based personalization.<br></p><h3>Legal Basis</h3><p>Consent (GDPR Art. 6(1)(a))<br></p><h3>Limitations</h3><p>Not for operational decisions (use source CRM directly); not for credit or risk decisions; PII handling under GDPR Art. 6(1)(a) consent basis.<br></p>', 'ACTIVE', aggregated_type_id, ready);

    INSERT INTO public.abstract_data_products (id, "name", namespace, description, domain_id, abstract_data_product_type, created_on, updated_on, deleted_at) VALUES (campaign_activation_dp_id, 'Campaign Activation', 'campaign-activation', 'Transforms enriched customer segments into channel-ready audience lists for targeted campaign execution across email, paid media, and loyalty channels.', marketing_id, 'data_products', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products (id, about, status, type_id, lifecycle_id) VALUES (campaign_activation_dp_id, '<h3>Value Proposition</h3><p>Transforms enriched customer segments from the Marketing Customer 360 into actionable, channel-ready audience lists. Enables marketing teams to execute highly targeted campaigns with measurable precision, reducing wasted spend and increasing conversion rates.<br></p><h3>User Consumption Mode</h3><p><strong>Operational:</strong> Designed for direct integration with marketing automation platforms and ad tech systems to activate audience segments in near real time.<br></p><h3>Recommended Use Cases</h3><ul><li><p><strong>Email Marketing:</strong> Automated lifecycle campaigns triggered by customer behavior signals.</p></li><li><p><strong>Paid Media:</strong> Lookalike audience creation and retargeting suppression lists.</p></li><li><p><strong>Loyalty Programs:</strong> Personalized reward offers based on RFM tier and purchase history.</p></li></ul><p></p><h3>Business Entities</h3><p><strong>Audience Segment:</strong> A named group of customers who share a behavioural profile (e.g. high-value lapsed buyers, at-risk loyalists) and are ready for activation through a specific marketing channel.<br><strong>Campaign:</strong> A coordinated marketing initiative targeting one or more audience segments across email, paid media, or loyalty channels, with a defined objective such as re-engagement or upsell.<br></p><h3>Business Process</h3><p>The Campaign Management team defines targeting criteria and activation rules in the campaign planning tool. These rules are applied to the Customer 360 to produce channel-ready audience lists — who gets which message, through which channel, and with what suppression rules applied. The lists are then exported to the marketing automation platform or ad platform for execution. This process runs daily ahead of scheduled campaign dispatches.<br></p><h3>Intended Use</h3><p>Activates segmented audiences from Customer 360 for campaign targeting across channels.<br></p><h3>Legal Basis</h3><p>Consent (GDPR Art. 6(1)(a))<br></p><h3>Limitations</h3><p>Customer PII must not be transmitted to third-party ad platforms in raw form. All audience exports must be hashed or anonymized in compliance with GDPR and CCPA requirements.<br></p>', 'ACTIVE', consumer_aligned_type_id, draft);

    INSERT INTO public.abstract_data_products (id, "name", namespace, description, domain_id, abstract_data_product_type, created_on, updated_on, deleted_at) VALUES (churn_model_dp_id, 'Churn Model', 'churn-model', 'Predicts the likelihood of customer churn using the unified customer view, enabling proactive retention interventions.', marketing_id, 'data_products', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products (id, about, status, type_id, lifecycle_id) VALUES (churn_model_dp_id, '<h3>Value Proposition</h3><p>Leverages the unified customer view from the Marketing Customer 360 to predict the likelihood of customer churn. Enables proactive retention interventions before customers disengage, directly improving Customer Lifetime Value and reducing acquisition costs.<br></p><h3>User Consumption Mode</h3><p><strong>Analytical & Operational:</strong> Scored daily and consumed by both the data science team for model iteration and marketing automation systems for real-time retention triggers.<br></p><h3>Recommended Use Cases</h3><ul><li><p><strong>Retention Marketing:</strong> Triggering win-back campaigns for high-risk customer segments.</p></li><li><p><strong>Customer Success:</strong> Prioritizing proactive outreach by customer health score.</p></li><li><p><strong>Product:</strong> Identifying product usage patterns correlated with churn risk.</p></li></ul><p></p><h3>Business Entities</h3><p><strong>Customer:</strong> The individual being scored for churn risk, identified by their customer_id from the Customer 360.<br><strong>Churn Score:</strong> A probabilistic risk estimate (0.0–1.0) that quantifies how likely a customer is to stop purchasing within the next 90 days. Derived from behavioural signals including purchase recency, order frequency, revenue trend, and last shipment status.<br></p><h3>Business Process</h3><p>The Data Science team trains and retrains the churn model quarterly using historical customer behaviour. Each night, the model scores all active customers against the latest Customer 360 snapshot. The resulting scores are published to the Retention Marketing team, who use them to trigger win-back campaigns for high-risk customers and to help the Customer Success team prioritise outreach. A score above 0.7 automatically enrols a customer into the retention journey.<br></p><h3>Intended Use</h3><p>Predicts likelihood of customer churn using unified customer, order and shipment history.<br></p><h3>Legal Basis</h3><p>Legitimate Interest (GDPR Art. 6(1)(f))<br></p><h3>Limitations</h3><p>Model outputs are probabilistic scores and must not be used as the sole basis for customer-facing decisions. Scores must be reviewed alongside supporting data before triggering any customer communication.<br></p>', 'ACTIVE', consumer_aligned_type_id, draft);

    -- Sales CRM Customers → mike_id
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_crm_customers_dp_id, mike_id, 'e43b6f7a-e776-49b2-9b51-117d8644d971', 'APPROVED', mike_id, timezone('utc'::text, CURRENT_TIMESTAMP), mike_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    -- Sales ERP Orders → john_id (unchanged)
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_erp_orders_dp_id, john_id, 'e43b6f7a-e776-49b2-9b51-117d8644d971', 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    -- Logistics WMS Shipments → david_id
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), logistics_wms_shipments_dp_id, david_id, 'e43b6f7a-e776-49b2-9b51-117d8644d971', 'APPROVED', david_id, timezone('utc'::text, CURRENT_TIMESTAMP), david_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    -- Marketing Customer 360 → sarah_id
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), marketing_customer_360_dp_id, sarah_id, 'e43b6f7a-e776-49b2-9b51-117d8644d971', 'APPROVED', sarah_id, timezone('utc'::text, CURRENT_TIMESTAMP), sarah_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    -- Campaign Activation → emma_id
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), campaign_activation_dp_id, emma_id, 'e43b6f7a-e776-49b2-9b51-117d8644d971', 'APPROVED', emma_id, timezone('utc'::text, CURRENT_TIMESTAMP), emma_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    -- Churn Model → bob_id (unchanged)
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), churn_model_dp_id, bob_id, 'e43b6f7a-e776-49b2-9b51-117d8644d971', 'APPROVED', bob_id, timezone('utc'::text, CURRENT_TIMESTAMP), bob_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- DATA OUTPUT CONFIGURATIONS
    SELECT gen_random_uuid() INTO sales_crm_customers_do_config_id;
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES (sales_crm_customers_do_config_id, 'PostgreSQLTechnicalAssetConfiguration');
    INSERT INTO public.postgresql_technical_asset_configurations (id, "database", "schema", "table", access_granularity, created_on, updated_on, deleted_at) VALUES (sales_crm_customers_do_config_id, 'dpp_demo', 'sales_crm_customers', '*', 'schema', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    SELECT gen_random_uuid() INTO sales_erp_orders_do_config_id;
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES (sales_erp_orders_do_config_id, 'PostgreSQLTechnicalAssetConfiguration');
    INSERT INTO public.postgresql_technical_asset_configurations (id, "database", "schema", "table", access_granularity, created_on, updated_on, deleted_at) VALUES (sales_erp_orders_do_config_id, 'dpp_demo', 'sales_erp_orders', '*', 'schema', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    SELECT gen_random_uuid() INTO logistics_wms_shipments_do_config_id;
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES (logistics_wms_shipments_do_config_id, 'PostgreSQLTechnicalAssetConfiguration');
    INSERT INTO public.postgresql_technical_asset_configurations (id, "database", "schema", "table", access_granularity, created_on, updated_on, deleted_at) VALUES (logistics_wms_shipments_do_config_id, 'dpp_demo', 'logistics_wms_shipments', '*', 'schema', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    SELECT gen_random_uuid() INTO marketing_customer_360_do_config_id;
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES (marketing_customer_360_do_config_id, 'PostgreSQLTechnicalAssetConfiguration');
    INSERT INTO public.postgresql_technical_asset_configurations (id, "database", "schema", "table", access_granularity, created_on, updated_on, deleted_at) VALUES (marketing_customer_360_do_config_id, 'dpp_demo', 'marketing_customer_360', '*', 'schema', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- campaign_activation
    SELECT gen_random_uuid() INTO campaign_activation_do_config_id;
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES (campaign_activation_do_config_id, 'PostgreSQLTechnicalAssetConfiguration');
    INSERT INTO public.postgresql_technical_asset_configurations (id, "database", "schema", "table", access_granularity, created_on, updated_on, deleted_at) VALUES (campaign_activation_do_config_id, 'dpp_demo', 'campaign_activation', '*', 'schema', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- churn_model
    SELECT gen_random_uuid() INTO churn_model_do_config_id;
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES (churn_model_do_config_id, 'PostgreSQLTechnicalAssetConfiguration');
    INSERT INTO public.postgresql_technical_asset_configurations (id, "database", "schema", "table", access_granularity, created_on, updated_on, deleted_at) VALUES (churn_model_do_config_id, 'dpp_demo', 'churn_model', '*', 'schema', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- DATA OUTPUTS
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES (gen_random_uuid(), 'sales-crm-customers', 'Sales CRM Customers', 'Customer account information', 'ACTIVE', postgresql_id, postgresql_service_id, sales_crm_customers_dp_id, NULL, sales_crm_customers_do_config_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, 'default') returning id INTO sales_crm_customers_do_id;
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES (gen_random_uuid(), 'sales-erp-orders', 'Sales ERP Orders', 'Order data', 'ACTIVE', postgresql_id, postgresql_service_id, sales_erp_orders_dp_id, NULL, sales_erp_orders_do_config_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, 'default') returning id INTO sales_erp_orders_do_id;
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES (gen_random_uuid(), 'logistics-wms-shipments', 'Logistics WMS Shipments', 'Shipment and delivery status', 'ACTIVE', postgresql_id, postgresql_service_id, logistics_wms_shipments_dp_id, NULL, logistics_wms_shipments_do_config_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, 'default') returning id INTO logistics_wms_shipments_do_id;
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES (gen_random_uuid(), 'marketing-customer-360', 'Customer 360', 'This SQL model generates a Customer 360 view by unifying data from CRM, ERP, and Logistics. It maps customer profiles to their full order history and real-time shipment statuses to provide a holistic view of the customer journey.', 'ACTIVE', postgresql_id, postgresql_service_id, marketing_customer_360_dp_id, NULL, marketing_customer_360_do_config_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, 'default') returning id INTO marketing_customer_360_do_id;

    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES (gen_random_uuid(), 'campaign-activation', 'Campaign Activation', 'Channel-ready audience segments for campaign execution', 'ACTIVE', postgresql_id, postgresql_service_id, campaign_activation_dp_id, NULL, campaign_activation_do_config_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, 'default') returning id INTO campaign_activation_do_id;

    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES (gen_random_uuid(), 'churn-model', 'Churn Scores', 'Customer churn probability scores', 'ACTIVE', postgresql_id, postgresql_service_id, churn_model_dp_id, NULL, churn_model_do_config_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, 'default') returning id INTO churn_model_do_id;

    -- Fixed dataset (output port) UUIDs
    sales_crm_customers_ds_id    := '22222222-0000-0000-0000-000000000001'::uuid;
    sales_erp_orders_ds_id       := '22222222-0000-0000-0000-000000000002'::uuid;
    logistics_wms_shipments_ds_id := '22222222-0000-0000-0000-000000000003'::uuid;
    marketing_customer_360_ds_id  := '22222222-0000-0000-0000-000000000004'::uuid;
    campaign_activation_ds_id     := '22222222-0000-0000-0000-000000000005'::uuid;
    churn_model_ds_id             := '22222222-0000-0000-0000-000000000006'::uuid;

    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at, lifecycle_id) VALUES (sales_crm_customers_ds_id, 'customers', sales_crm_customers_dp_id, 'Customers', 'Customer account information from the CRM', '<p>The canonical source of truth for customer identity across the organisation. Sourced directly from the CRM and refreshed daily, this dataset provides clean, deduplicated records — including customer names, contact details, account status, and registration history. All downstream data products reference back to this dataset for customer identity resolution. Records are validated and enriched with standardised contact information before publication.<br></p><h3>Technical Interface</h3><p>Exposed as PostgreSQL schema <code>dpp_demo.sales_crm_customers</code>. Request access through the Data Product Portal — connection credentials are provisioned after approval.<br></p><h3>Python Quick Start</h3><pre><code>import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://{user}:{password}@{host}:{port}/dpp_demo")
df = pd.read_sql(
    "SELECT customer_id, first_name, last_name, email, signup_date "
    "FROM sales_crm_customers.customers "
    "WHERE signup_date >= CURRENT_DATE - INTERVAL ''90 days''",
    engine,
)</code></pre><h3>dbt Quick Start</h3><p>Add to your <code>sources.yml</code> to reference this dataset in dbt:</p><pre><code>sources:
  - name: sales_crm_customers
    database: dpp_demo
    schema: sales_crm_customers
    tables:
      - name: customers</code></pre>', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, ready);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at, lifecycle_id) VALUES (sales_erp_orders_ds_id, 'orders', sales_erp_orders_dp_id, 'Orders', 'Order data from the ERP system', '<p>The complete order history from the ERP system, covering every confirmed transaction from initial placement through final invoicing. Each record represents a commercial transaction tied to a customer, capturing what was ordered, at what price, when, and the current order status. This dataset is the primary source for revenue reporting, commission calculation, and demand forecasting across the business.<br></p><h3>Technical Interface</h3><p>Exposed as PostgreSQL schema <code>dpp_demo.sales_erp_orders</code>. Request access through the Data Product Portal — connection credentials are provisioned after approval.<br></p><h3>Python Quick Start</h3><pre><code>import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://{user}:{password}@{host}:{port}/dpp_demo")
df = pd.read_sql(
    "SELECT order_id, customer_id, order_date, total_amount "
    "FROM sales_erp_orders.orders "
    "WHERE order_date >= CURRENT_DATE - INTERVAL ''30 days''",
    engine,
)</code></pre><h3>dbt Quick Start</h3><p>Add to your <code>sources.yml</code> to reference this dataset in dbt:</p><pre><code>sources:
  - name: sales_erp_orders
    database: dpp_demo
    schema: sales_erp_orders
    tables:
      - name: orders</code></pre>', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, ready);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at, lifecycle_id) VALUES (logistics_wms_shipments_ds_id, 'shipments', logistics_wms_shipments_dp_id, 'Shipments', 'Shipment and delivery status from the WMS', '<p>End-to-end shipment tracking from warehouse dispatch to final customer delivery, refreshed hourly from WMS scan events. Each record represents a physical dispatch event associated with a confirmed order, capturing carrier details, key shipment milestones, and the current delivery status. This is the authoritative source for delivery performance monitoring, carrier SLA measurement, and customer service enquiry resolution.<br></p><h3>Technical Interface</h3><p>Exposed as PostgreSQL schema <code>dpp_demo.logistics_wms_shipments</code>. Request access through the Data Product Portal — connection credentials are provisioned after approval.<br></p><h3>Python Quick Start</h3><pre><code>import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://{user}:{password}@{host}:{port}/dpp_demo")
df = pd.read_sql(
    "SELECT shipment_id, order_ref, shipped_date, delivery_status "
    "FROM logistics_wms_shipments.shipments "
    "WHERE delivery_status != ''DELIVERED''",
    engine,
)</code></pre><h3>dbt Quick Start</h3><p>Add to your <code>sources.yml</code> to reference this dataset in dbt:</p><pre><code>sources:
  - name: logistics_wms_shipments
    database: dpp_demo
    schema: logistics_wms_shipments
    tables:
      - name: shipments</code></pre>', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, ready);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at, lifecycle_id) VALUES (marketing_customer_360_ds_id, 'customer-360', marketing_customer_360_dp_id, 'Customer 360', 'This SQL model generates a Customer 360 view by unifying data from CRM, ERP, and Logistics.', '<p>A unified view of every customer''s commercial relationship with the company, assembled by joining CRM identity data, ERP order history, and WMS shipment status into a single, consent-governed record per customer. Enriched with pre-computed RFM (Recency, Frequency, Monetary) segmentation, this dataset is the primary analytical asset for marketing campaign planning, data science modelling, and customer support workflows.<br></p><h3>Technical Interface</h3><p>Exposed as PostgreSQL schema <code>dpp_demo.marketing_customer_360</code>. Request access through the Data Product Portal — connection credentials are provisioned after approval.<br></p><h3>Python Quick Start</h3><pre><code>import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://{user}:{password}@{host}:{port}/dpp_demo")
df = pd.read_sql(
    "SELECT customer_id, first_name, last_name, email, "
    "       total_orders, total_revenue, rfm_segment "
    "FROM marketing_customer_360.customer_360 "
    "WHERE rfm_segment IN (''Champions'', ''At Risk'')",
    engine,
)</code></pre><h3>dbt Quick Start</h3><p>Add to your <code>sources.yml</code> to reference this dataset in dbt:</p><pre><code>sources:
  - name: marketing_customer_360
    database: dpp_demo
    schema: marketing_customer_360
    tables:
      - name: customer_360</code></pre>', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, ready);

    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at, lifecycle_id) VALUES (campaign_activation_ds_id, 'audience-segments', campaign_activation_dp_id, 'Audience Segments', 'Channel-ready audience segments for targeted campaign execution', '<p>Channel-ready audience lists derived from the Customer 360, prepared for direct export to marketing automation platforms and ad tech systems. Each record associates a customer with a named behavioural segment and a target activation channel, with suppression rules applied. The dataset is regenerated daily ahead of scheduled campaign dispatches and is the handoff point between analytics and campaign execution.<br></p><h3>Technical Interface</h3><p>Exposed as PostgreSQL schema <code>dpp_demo.campaign_activation</code>. Request access through the Data Product Portal — connection credentials are provisioned after approval.<br></p><h3>Python Quick Start</h3><pre><code>import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://{user}:{password}@{host}:{port}/dpp_demo")
df = pd.read_sql(
    "SELECT segment_id, customer_id, segment_name, channel, activation_date "
    "FROM campaign_activation.audience_segments "
    "WHERE activation_date = CURRENT_DATE AND channel = ''email''",
    engine,
)</code></pre><h3>dbt Quick Start</h3><p>Add to your <code>sources.yml</code> to reference this dataset in dbt:</p><pre><code>sources:
  - name: campaign_activation
    database: dpp_demo
    schema: campaign_activation
    tables:
      - name: audience_segments</code></pre>', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, draft);

    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at, lifecycle_id) VALUES (churn_model_ds_id, 'churn-scores', churn_model_dp_id, 'Churn Scores', 'Customer churn probability scores from the prediction model', '<p>Daily churn risk scores for every active customer, produced by a machine learning model trained on unified customer behaviour from the Customer 360. Each record provides a probabilistic churn score, a derived risk tier, and supporting metadata such as model version and score timestamp. Customers with a score above 0.7 are automatically enrolled into the retention journey — scores must not be the sole basis for any customer-facing decision.<br></p><h3>Technical Interface</h3><p>Exposed as PostgreSQL schema <code>dpp_demo.churn_model</code>. Request access through the Data Product Portal — connection credentials are provisioned after approval.<br></p><h3>Python Quick Start</h3><pre><code>import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://{user}:{password}@{host}:{port}/dpp_demo")
df = pd.read_sql(
    "SELECT customer_id, churn_score, churn_risk_tier, scored_at "
    "FROM churn_model.churn_scores "
    "WHERE churn_score > 0.7 "
    "ORDER BY churn_score DESC",
    engine,
)</code></pre><h3>dbt Quick Start</h3><p>Add to your <code>sources.yml</code> to reference this dataset in dbt:</p><pre><code>sources:
  - name: churn_model
    database: dpp_demo
    schema: churn_model
    tables:
      - name: churn_scores</code></pre>', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, draft);

    -- sales_crm_customers → mike_id
    INSERT INTO public.role_assignments_dataset (id, dataset_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_crm_customers_ds_id, mike_id, '9a9d7deb-14d9-4257-a986-7900aa70ef8f', 'APPROVED', mike_id, timezone('utc'::text, CURRENT_TIMESTAMP), mike_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    -- sales_erp_orders → john_id (unchanged)
    INSERT INTO public.role_assignments_dataset (id, dataset_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_erp_orders_ds_id, john_id, '9a9d7deb-14d9-4257-a986-7900aa70ef8f', 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    -- logistics_wms_shipments → david_id
    INSERT INTO public.role_assignments_dataset (id, dataset_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), logistics_wms_shipments_ds_id, david_id, '9a9d7deb-14d9-4257-a986-7900aa70ef8f', 'APPROVED', david_id, timezone('utc'::text, CURRENT_TIMESTAMP), david_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    -- marketing_customer_360 → sarah_id
    INSERT INTO public.role_assignments_dataset (id, dataset_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), marketing_customer_360_ds_id, sarah_id, '9a9d7deb-14d9-4257-a986-7900aa70ef8f', 'APPROVED', sarah_id, timezone('utc'::text, CURRENT_TIMESTAMP), sarah_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    -- campaign_activation → emma_id
    INSERT INTO public.role_assignments_dataset (id, dataset_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), campaign_activation_ds_id, emma_id, '9a9d7deb-14d9-4257-a986-7900aa70ef8f', 'APPROVED', emma_id, timezone('utc'::text, CURRENT_TIMESTAMP), emma_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    -- churn_model → bob_id (unchanged)
    INSERT INTO public.role_assignments_dataset (id, dataset_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), churn_model_ds_id, bob_id, '9a9d7deb-14d9-4257-a986-7900aa70ef8f', 'APPROVED', bob_id, timezone('utc'::text, CURRENT_TIMESTAMP), bob_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- DATA OUTPUTS - DATASETS
    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_crm_customers_do_id, sales_crm_customers_ds_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_erp_orders_do_id, sales_erp_orders_ds_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), logistics_wms_shipments_do_id, logistics_wms_shipments_ds_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), marketing_customer_360_do_id, marketing_customer_360_ds_id, 'APPROVED', alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), campaign_activation_do_id, campaign_activation_ds_id, 'APPROVED', alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), churn_model_do_id, churn_model_ds_id, 'APPROVED', bob_id, timezone('utc'::text, CURRENT_TIMESTAMP), bob_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- INPUT PORTS
    -- Marketing Customer 360 consumes: Customers, Orders, Shipments (sarah_id requests + approves via her ownership of MC360)
    INSERT INTO public.input_ports (id, justification, status, requested_on, approved_on, denied_on, consuming_abstract_data_product_id, dataset_id, requested_by_id, approved_by_id, denied_by_id) VALUES (gen_random_uuid(), 'Access is required to integrate Customer, Order, and Shipment data into the Marketing Customer 360. This enables RFM modeling to increase Customer Lifetime Value (LTV), improves ROAS by suppressing ads for recent purchasers, and allows for proactive retention triggers based on delivery status.', 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, marketing_customer_360_dp_id, sales_crm_customers_ds_id, sarah_id, sarah_id, NULL);
    INSERT INTO public.input_ports (id, justification, status, requested_on, approved_on, denied_on, consuming_abstract_data_product_id, dataset_id, requested_by_id, approved_by_id, denied_by_id) VALUES (gen_random_uuid(), 'Access is required to integrate Customer, Order, and Shipment data into the Marketing Customer 360. This enables RFM modeling to increase Customer Lifetime Value (LTV), improves ROAS by suppressing ads for recent purchasers, and allows for proactive retention triggers based on delivery status.', 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, marketing_customer_360_dp_id, sales_erp_orders_ds_id, sarah_id, sarah_id, NULL);
    INSERT INTO public.input_ports (id, justification, status, requested_on, approved_on, denied_on, consuming_abstract_data_product_id, dataset_id, requested_by_id, approved_by_id, denied_by_id) VALUES (gen_random_uuid(), 'Access is required to integrate Customer, Order, and Shipment data into the Marketing Customer 360. This enables RFM modeling to increase Customer Lifetime Value (LTV), improves ROAS by suppressing ads for recent purchasers, and allows for proactive retention triggers based on delivery status.', 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, marketing_customer_360_dp_id, logistics_wms_shipments_ds_id, sarah_id, sarah_id, NULL);
    -- Campaign Activation consumes: Customer 360 (emma_id requests; sarah_id approves as MC360 owner)
    INSERT INTO public.input_ports (id, justification, status, requested_on, approved_on, denied_on, consuming_abstract_data_product_id, dataset_id, requested_by_id, approved_by_id, denied_by_id) VALUES (gen_random_uuid(), 'Access to the Customer 360 is required to build enriched audience segments for targeted campaign activation across email, paid media, and loyalty channels.', 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, campaign_activation_dp_id, marketing_customer_360_ds_id, emma_id, sarah_id, NULL);
    -- Churn Model consumes: Customer 360 (bob_id requests; sarah_id approves as MC360 owner)
    INSERT INTO public.input_ports (id, justification, status, requested_on, approved_on, denied_on, consuming_abstract_data_product_id, dataset_id, requested_by_id, approved_by_id, denied_by_id) VALUES (gen_random_uuid(), 'Access to the Customer 360 is required to train and score the churn prediction model using unified customer behavior, purchase history, and delivery data.', 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, churn_model_dp_id, marketing_customer_360_ds_id, bob_id, sarah_id, NULL);

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

    -- Customer 360 usage
    -- campaign_activation: ~8,400/month → 385/weekday
    INSERT INTO public.dataset_query_stats_daily (date, dataset_id, consumer_data_product_id, query_count)
    SELECT gs::date, marketing_customer_360_ds_id, campaign_activation_dp_id, 385
    FROM generate_series((CURRENT_DATE - INTERVAL '3 months')::date, CURRENT_DATE - 1, INTERVAL '1 day') AS gs
    WHERE EXTRACT(ISODOW FROM gs) BETWEEN 1 AND 5;

    -- churn_model: ~3,100/month → 142/weekday
    INSERT INTO public.dataset_query_stats_daily (date, dataset_id, consumer_data_product_id, query_count)
    SELECT gs::date, marketing_customer_360_ds_id, churn_model_dp_id, 142
    FROM generate_series((CURRENT_DATE - INTERVAL '3 months')::date, CURRENT_DATE - 1, INTERVAL '1 day') AS gs
    WHERE EXTRACT(ISODOW FROM gs) BETWEEN 1 AND 5;

    -- ------------------------------------------------------------------------------------------------
    -- END of Insert dynamic dataset query stats
    -- ------------------------------------------------------------------------------------------------

    -- ------------------------------------------------------------------------------------------------
    -- START of Insert output port cost records
    -- ------------------------------------------------------------------------------------------------

    -- Sales CRM Customers: ~36 compute / ~12 storage / ~57 platform overhead per month
    INSERT INTO public.output_port_cost_records (id, output_port_id, recorded_at, compute_cost, storage_cost, platform_overhead_cost)
    SELECT
        gen_random_uuid(),
        sales_crm_customers_ds_id,
        gs::date,
        1.1800 + (EXTRACT(DOW FROM gs) * 0.0300),
        0.3900 + (EXTRACT(DOW FROM gs) * 0.0050),
        1.8500 + (EXTRACT(DOW FROM gs) * 0.0200)
    FROM generate_series((CURRENT_DATE - INTERVAL '3 months')::date, CURRENT_DATE - 1, INTERVAL '1 day') AS gs;

    -- Sales ERP Orders: ~55 compute / ~16 storage / ~57 platform overhead per month
    INSERT INTO public.output_port_cost_records (id, output_port_id, recorded_at, compute_cost, storage_cost, platform_overhead_cost)
    SELECT
        gen_random_uuid(),
        sales_erp_orders_ds_id,
        gs::date,
        1.7500 + (EXTRACT(DOW FROM gs) * 0.0400),
        0.5100 + (EXTRACT(DOW FROM gs) * 0.0060),
        1.8500 + (EXTRACT(DOW FROM gs) * 0.0200)
    FROM generate_series((CURRENT_DATE - INTERVAL '3 months')::date, CURRENT_DATE - 1, INTERVAL '1 day') AS gs;

    -- Logistics WMS Shipments: ~23 compute / ~9 storage / ~57 platform overhead per month
    INSERT INTO public.output_port_cost_records (id, output_port_id, recorded_at, compute_cost, storage_cost, platform_overhead_cost)
    SELECT
        gen_random_uuid(),
        logistics_wms_shipments_ds_id,
        gs::date,
        0.7300 + (EXTRACT(DOW FROM gs) * 0.0200),
        0.2700 + (EXTRACT(DOW FROM gs) * 0.0040),
        1.8500 + (EXTRACT(DOW FROM gs) * 0.0200)
    FROM generate_series((CURRENT_DATE - INTERVAL '3 months')::date, CURRENT_DATE - 1, INTERVAL '1 day') AS gs;

    -- Marketing Customer 360: ~48 compute / ~15 storage / ~57 platform overhead per month
    INSERT INTO public.output_port_cost_records (id, output_port_id, recorded_at, compute_cost, storage_cost, platform_overhead_cost)
    SELECT
        gen_random_uuid(),
        marketing_customer_360_ds_id,
        gs::date,
        1.5200 + (EXTRACT(DOW FROM gs) * 0.0350),
        0.4700 + (EXTRACT(DOW FROM gs) * 0.0055),
        1.8500 + (EXTRACT(DOW FROM gs) * 0.0200)
    FROM generate_series((CURRENT_DATE - INTERVAL '3 months')::date, CURRENT_DATE - 1, INTERVAL '1 day') AS gs;

    -- ------------------------------------------------------------------------------------------------
    -- END of Insert output port cost records
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

    INSERT INTO public.dataset_curated_queries (output_port_id, title, description, query_text, sort_order)
    VALUES (
        marketing_customer_360_ds_id,
        'High-Value Customer Segments',
        'Retrieve top customers by total revenue for loyalty and campaign targeting.',
        'SELECT customer_id, first_name, last_name, email, total_orders, total_revenue, rfm_segment
         FROM customer_360
         WHERE rfm_segment IN (''Champions'', ''Loyal Customers'')
         ORDER BY total_revenue DESC
         LIMIT 100;',
        0
    );

    -- ------------------------------------------------------------------------------------------------
    -- Freshness SLOs
    -- ------------------------------------------------------------------------------------------------
    -- sales_erp_orders: 06:00 UTC deadline, last refreshed 1 hour ago → fresh
    -- sales_crm_customers: 07:00 UTC deadline, last refreshed 2 hours ago → fresh
    -- logistics_wms_shipments: 05:00 UTC deadline, last refreshed 2 days ago → STALE
    -- marketing_customer_360: 06:00 UTC deadline, last refreshed 18 hours ago → WARNING (ran on stale logistics)
    INSERT INTO public.output_port_freshness_slos (id, output_port_id, deadline_time, created_at, updated_at)
    VALUES
        (gen_random_uuid(), sales_erp_orders_ds_id,           '06:00:00'::time, NOW(), NOW()),
        (gen_random_uuid(), sales_crm_customers_ds_id,        '07:00:00'::time, NOW(), NOW()),
        (gen_random_uuid(), logistics_wms_shipments_ds_id,    '05:00:00'::time, NOW(), NOW()),
        (gen_random_uuid(), marketing_customer_360_ds_id,     '06:00:00'::time, NOW(), NOW());

    INSERT INTO public.output_port_freshness_observations (id, output_port_id, last_refreshed_at, created_at)
    VALUES
        (gen_random_uuid(), sales_erp_orders_ds_id,           NOW() - INTERVAL '1 hour',  NOW()),
        (gen_random_uuid(), sales_crm_customers_ds_id,        NOW() - INTERVAL '2 hours', NOW()),
        (gen_random_uuid(), logistics_wms_shipments_ds_id,    NOW() - INTERVAL '2 days',  NOW()),
        (gen_random_uuid(), marketing_customer_360_ds_id,     NOW() - INTERVAL '18 hours', NOW());

    -- ------------------------------------------------------------------------------------------------
    -- DATA QUALITY SUMMARIES
    -- ------------------------------------------------------------------------------------------------
    INSERT INTO public.output_port_data_quality_summaries (id, output_port_id, overall_status, assets_with_checks, assets_with_issues, dimensions, created_at)
    VALUES (gen_random_uuid(), sales_crm_customers_ds_id, 'success', 3, 0, '{"completeness": "success", "validity": "success", "freshness": "success"}'::jsonb, NOW() - INTERVAL '1 hour')
    RETURNING id INTO sales_crm_customers_dq_id;

    INSERT INTO public.output_port_data_quality_summaries (id, output_port_id, overall_status, assets_with_checks, assets_with_issues, dimensions, created_at)
    VALUES (gen_random_uuid(), sales_erp_orders_ds_id, 'success', 4, 0, '{"completeness": "success", "validity": "success", "freshness": "success"}'::jsonb, NOW() - INTERVAL '2 hours')
    RETURNING id INTO sales_erp_orders_dq_id;

    INSERT INTO public.output_port_data_quality_summaries (id, output_port_id, overall_status, assets_with_checks, assets_with_issues, dimensions, created_at)
    VALUES (gen_random_uuid(), logistics_wms_shipments_ds_id, 'success', 4, 0, '{"completeness": "success", "validity": "success", "freshness": "success"}'::jsonb, NOW() - INTERVAL '30 minutes')
    RETURNING id INTO logistics_wms_shipments_dq_id;

    INSERT INTO public.output_port_data_quality_summaries (id, output_port_id, overall_status, assets_with_checks, assets_with_issues, dimensions, created_at)
    VALUES (gen_random_uuid(), marketing_customer_360_ds_id, 'warning', 10, 1, '{"completeness": "success", "validity": "success", "freshness": "warning", "uniqueness": "success"}'::jsonb, NOW() - INTERVAL '3 hours')
    RETURNING id INTO marketing_customer_360_dq_id;

    INSERT INTO public.output_port_data_quality_summaries (id, output_port_id, overall_status, assets_with_checks, assets_with_issues, dimensions, created_at)
    VALUES (gen_random_uuid(), campaign_activation_ds_id, 'success', 2, 0, '{"completeness": "success", "validity": "success"}'::jsonb, NOW() - INTERVAL '4 hours')
    RETURNING id INTO campaign_activation_dq_id;

    INSERT INTO public.output_port_data_quality_summaries (id, output_port_id, overall_status, assets_with_checks, assets_with_issues, dimensions, created_at)
    VALUES (gen_random_uuid(), churn_model_ds_id, 'success', 2, 0, '{"completeness": "success", "validity": "success"}'::jsonb, NOW() - INTERVAL '5 hours')
    RETURNING id INTO churn_model_dq_id;

    -- DATA QUALITY TECHNICAL ASSETS
    INSERT INTO public.data_quality_technical_assets (name, status, data_quality_summary_id) VALUES
        ('customers', 'success', sales_crm_customers_dq_id),
        ('customers_pii', 'success', sales_crm_customers_dq_id),
        ('customers_contact', 'success', sales_crm_customers_dq_id);

    INSERT INTO public.data_quality_technical_assets (name, status, data_quality_summary_id) VALUES
        ('orders', 'success', sales_erp_orders_dq_id),
        ('order_lines', 'success', sales_erp_orders_dq_id),
        ('order_status', 'success', sales_erp_orders_dq_id),
        ('order_payments', 'success', sales_erp_orders_dq_id);

    INSERT INTO public.data_quality_technical_assets (name, status, data_quality_summary_id) VALUES
        ('shipments', 'success', logistics_wms_shipments_dq_id),
        ('shipment_events', 'success', logistics_wms_shipments_dq_id),
        ('carriers', 'success', logistics_wms_shipments_dq_id),
        ('delivery_addresses', 'success', logistics_wms_shipments_dq_id);

    INSERT INTO public.data_quality_technical_assets (name, status, data_quality_summary_id) VALUES
        ('customer_360', 'success', marketing_customer_360_dq_id),
        ('rfm_segments', 'success', marketing_customer_360_dq_id);

    INSERT INTO public.data_quality_technical_assets (name, status, data_quality_summary_id) VALUES
        ('audience_segments', 'success', campaign_activation_dq_id),
        ('suppression_lists', 'success', campaign_activation_dq_id);

    INSERT INTO public.data_quality_technical_assets (name, status, data_quality_summary_id) VALUES
        ('churn_scores', 'success', churn_model_dq_id),
        ('model_features', 'success', churn_model_dq_id);

end $$;
