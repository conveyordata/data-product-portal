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

begin
    TRUNCATE TABLE public.input_ports CASCADE;
    TRUNCATE TABLE public.datasets CASCADE;
    TRUNCATE TABLE public.abstract_data_products CASCADE;
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
    TRUNCATE TABLE public.output_port_cost_records CASCADE;
    TRUNCATE TABLE public.output_port_freshness_slos CASCADE;
    TRUNCATE TABLE public.output_port_freshness_observations CASCADE;
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
    INSERT INTO public.data_products (id, about, status, type_id, lifecycle_id) VALUES (sales_crm_customers_dp_id, '<h3>Value Proposition</h3>
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
<p><strong>Limitations:</strong> Not authorized for external regulatory reporting. Handing of PII must strictly adhere to the corporate GDPR compliance framework.</p>', 'ACTIVE', source_aligned_type_id, ready);

    INSERT INTO public.abstract_data_products (id, "name", namespace, description, domain_id, abstract_data_product_type, created_on, updated_on, deleted_at) VALUES (sales_erp_orders_dp_id, 'Sales ERP Orders', 'sales-erp-orders', 'Provides real-time order data from our ERP system.', sales_id, 'data_products', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products (id, about, status, type_id, lifecycle_id) VALUES (sales_erp_orders_dp_id, '<h3>Value Proposition</h3>
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
<p><strong>Limitations:</strong> This is a real-time feed and may include pending transactions. It is not the master record for audited financial statements. Historical corrections can occur within a 24-hour window.</p>', 'ACTIVE', source_aligned_type_id, ready);

    INSERT INTO public.abstract_data_products (id, "name", namespace, description, domain_id, abstract_data_product_type, created_on, updated_on, deleted_at) VALUES (logistics_wms_shipments_dp_id, 'Logistics WMS Shipments', 'logistics-wms-shipments', 'Tracks order shipment and delivery status from the warehouse.', logistics_id, 'data_products', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products (id, about, status, type_id, lifecycle_id) VALUES (logistics_wms_shipments_dp_id, '<h3>Value Proposition</h3>
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
<p><strong>Limitations:</strong> Data accuracy is dependent on third-party carrier scan events. Not suitable as sole evidence in legal delivery disputes without secondary carrier documentation.</p>', 'ACTIVE', source_aligned_type_id, ready);

    INSERT INTO public.abstract_data_products (id, "name", namespace, description, domain_id, abstract_data_product_type, created_on, updated_on, deleted_at) VALUES (marketing_customer_360_dp_id, 'Marketing Customer 360', 'marketing-customer-360', 'A consolidated view of customer activity, combining customer profiles, order history, and shipment status for marketing analysis.', marketing_id, 'data_products', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products (id, about, status, type_id, lifecycle_id) VALUES (marketing_customer_360_dp_id, '<h3>Value Proposition</h3>
<p>This data product consolidates fragmented customer signals into a single, authoritative view. By unifying CRM profiles with transactional order history and real-time shipment status, it empowers marketing, data science, and support teams to execute with precision and build lasting customer relationships.<br></p>

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
<p><strong>Limitations:</strong> Not authorized for external regulatory reporting. Handling of PII must strictly adhere to the corporate GDPR compliance framework.</p>', 'ACTIVE', aggregated_type_id, ready);

    INSERT INTO public.abstract_data_products (id, "name", namespace, description, domain_id, abstract_data_product_type, created_on, updated_on, deleted_at) VALUES (campaign_activation_dp_id, 'Campaign Activation', 'campaign-activation', 'Transforms enriched customer segments into channel-ready audience lists for targeted campaign execution across email, paid media, and loyalty channels.', marketing_id, 'data_products', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products (id, about, status, type_id, lifecycle_id) VALUES (campaign_activation_dp_id, '<h3>Value Proposition</h3>
<p>Transforms enriched customer segments from the Marketing Customer 360 into actionable, channel-ready audience lists. Enables marketing teams to execute highly targeted campaigns with measurable precision, reducing wasted spend and increasing conversion rates.<br></p>

<h3>User Consumption Mode</h3>
<p><strong>Operational:</strong> Designed for direct integration with marketing automation platforms and ad tech systems to activate audience segments in near real time.<br></p>

<h3>Recommended Use Cases</h3>
<p><ul>
  <li><strong>Email Marketing:</strong> Automated lifecycle campaigns triggered by customer behavior signals.</li>
  <li><strong>Paid Media:</strong> Lookalike audience creation and retargeting suppression lists.</li>
  <li><strong>Loyalty Programs:</strong> Personalized reward offers based on RFM tier and purchase history.</li>
</ul></p>

<h3>Terms of Use</h3>
<p><strong>Usage:</strong> Approved for internal marketing automation and paid media activation workflows.</p>
<p><strong>Limitations:</strong> Customer PII must not be transmitted to third-party ad platforms in raw form. All audience exports must be hashed or anonymized in compliance with GDPR and CCPA requirements.</p>', 'ACTIVE', consumer_aligned_type_id, draft);

    INSERT INTO public.abstract_data_products (id, "name", namespace, description, domain_id, abstract_data_product_type, created_on, updated_on, deleted_at) VALUES (churn_model_dp_id, 'Churn Model', 'churn-model', 'Predicts the likelihood of customer churn using the unified customer view, enabling proactive retention interventions.', marketing_id, 'data_products', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products (id, about, status, type_id, lifecycle_id) VALUES (churn_model_dp_id, '<h3>Value Proposition</h3>
<p>Leverages the unified customer view from the Marketing Customer 360 to predict the likelihood of customer churn. Enables proactive retention interventions before customers disengage, directly improving Customer Lifetime Value and reducing acquisition costs.<br></p>

<h3>User Consumption Mode</h3>
<p><strong>Analytical & Operational:</strong> Scored daily and consumed by both the data science team for model iteration and marketing automation systems for real-time retention triggers.<br></p>

<h3>Recommended Use Cases</h3>
<p><ul>
  <li><strong>Retention Marketing:</strong> Triggering win-back campaigns for high-risk customer segments.</li>
  <li><strong>Customer Success:</strong> Prioritizing proactive outreach by customer health score.</li>
  <li><strong>Product:</strong> Identifying product usage patterns correlated with churn risk.</li>
</ul></p>

<h3>Terms of Use</h3>
<p><strong>Usage:</strong> Approved for internal retention analysis, marketing automation, and product analytics.</p>
<p><strong>Limitations:</strong> Model outputs are probabilistic scores and must not be used as the sole basis for customer-facing decisions. Scores should be reviewed alongside supporting data before triggering any customer communication.</p>', 'ACTIVE', consumer_aligned_type_id, draft);

    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_crm_customers_dp_id, john_id, 'e43b6f7a-e776-49b2-9b51-117d8644d971', 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_erp_orders_dp_id, john_id, 'e43b6f7a-e776-49b2-9b51-117d8644d971', 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), logistics_wms_shipments_dp_id, john_id, 'e43b6f7a-e776-49b2-9b51-117d8644d971', 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), marketing_customer_360_dp_id, alice_id, 'e43b6f7a-e776-49b2-9b51-117d8644d971', 'APPROVED', alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), campaign_activation_dp_id, alice_id, 'e43b6f7a-e776-49b2-9b51-117d8644d971', 'APPROVED', alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
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

    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at, lifecycle_id) VALUES (sales_crm_customers_ds_id, 'customers', sales_crm_customers_dp_id, 'Customers', 'Customer account information from the CRM', '<p><strong>Version:</strong> 1.0.0 &nbsp;|&nbsp; <strong>Freshness:</strong> Daily (Morning sync)</p><p>This dataset contains curated customer information from the Sales CRM, providing a single source of truth for customer identity and contact details.</p><br><h3>How to Use</h3><p>Use this dataset to enrich sales data with customer demographic information or for marketing campaign targeting. Join with the <code>Orders</code> dataset on <code>customer_id</code>.</p><br><h3>Table Schema</h3><table><thead><tr><th>Column Name</th><th>Type</th><th>Description</th></tr></thead><tbody><tr><td>id</td><td>Integer</td><td>Unique identifier for the customer.</td></tr><tr><td>first_name</td><td>String</td><td>Customer''s first name.</td></tr><tr><td>last_name</td><td>String</td><td>Customer''s last name.</td></tr><tr><td>email</td><td>String</td><td>Primary contact email address.</td></tr><tr><td>signup_date</td><td>Timestamp</td><td>Timestamp when the customer registered.</td></tr></tbody></table>', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, ready);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at, lifecycle_id) VALUES (sales_erp_orders_ds_id, 'orders', sales_erp_orders_dp_id, 'Orders', 'Order data from the ERP system', '<p><strong>Version:</strong> 1.1.0 &nbsp;|&nbsp; <strong>Freshness:</strong> Real-time (near real-time via ERP hooks)</p><p>Provides detailed transaction history for all sales orders processed through the ERP system.</p><br><h3>How to Use</h3><p>This dataset is the primary source for revenue analysis and order volume tracking. It can be joined with <code>Customers</code> for customer-level insights or <code>Shipments</code> for fulfillment tracking.</p><br><h3>Table Schema</h3><table><thead><tr><th>Column Name</th><th>Type</th><th>Description</th></tr></thead><tbody><tr><td>order_id</td><td>Integer</td><td>Unique identifier for the order.</td></tr><tr><td>customer_id</td><td>Integer</td><td>Reference to the customer who placed the order.</td></tr><tr><td>order_date</td><td>Timestamp</td><td>Timestamp of order placement.</td></tr><tr><td>total_amount</td><td>Decimal</td><td>Total monetary value of the order.</td></tr></tbody></table>', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, ready);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at, lifecycle_id) VALUES (logistics_wms_shipments_ds_id, 'shipments', logistics_wms_shipments_dp_id, 'Shipments', 'Shipment and delivery status from the WMS', '<p><strong>Version:</strong> 1.0.2 &nbsp;|&nbsp; <strong>Freshness:</strong> Hourly updates</p><p>Tracks the fulfillment lifecycle of orders, from warehouse dispatch to final delivery status.</p><br><h3>How to Use</h3><p>Utilize this data to monitor delivery times, identify shipping bottlenecks, and calculate order fulfillment rates. Join with <code>Orders</code> on <code>order_ref</code>.</p><br><h3>Table Schema</h3><table><thead><tr><th>Column Name</th><th>Type</th><th>Description</th></tr></thead><tbody><tr><td>shipment_id</td><td>Integer</td><td>Unique identifier for the shipment record.</td></tr><tr><td>order_ref</td><td>Integer</td><td>Reference to the corresponding ERP order.</td></tr><tr><td>shipped_date</td><td>Timestamp</td><td>Timestamp when the package left the warehouse.</td></tr><tr><td>delivery_status</td><td>String</td><td>Current status of the delivery (e.g., Shipped, In Transit, Delivered).</td></tr></tbody></table>', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, ready);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at, lifecycle_id) VALUES (marketing_customer_360_ds_id, 'customer-360', marketing_customer_360_dp_id, 'Customer 360', 'This SQL model generates a Customer 360 view by unifying data from CRM, ERP, and Logistics.', '<p><strong>Version:</strong> 1.0.0 &nbsp;|&nbsp; <strong>Freshness:</strong> Daily (Morning sync)</p><p>This dataset unifies customer profiles, order history, and shipment status into a comprehensive Customer 360 view optimized for marketing analysis and activation.</p><br><h3>How to Use</h3><p>Use this dataset for customer segmentation, RFM modeling, churn prediction, and campaign activation. Join on <code>customer_id</code> for customer-level insights. It serves as the primary input for all downstream marketing data products.</p><br><h3>Table Schema</h3><table><thead><tr><th>Column Name</th><th>Type</th><th>Description</th></tr></thead><tbody><tr><td>customer_id</td><td>Integer</td><td>Unique identifier for the customer.</td></tr><tr><td>first_name</td><td>String</td><td>Customer''s first name.</td></tr><tr><td>last_name</td><td>String</td><td>Customer''s last name.</td></tr><tr><td>email</td><td>String</td><td>Primary contact email address.</td></tr><tr><td>signup_date</td><td>Timestamp</td><td>Timestamp when the customer registered.</td></tr><tr><td>total_orders</td><td>Integer</td><td>Total number of orders placed by the customer.</td></tr><tr><td>total_revenue</td><td>Decimal</td><td>Total monetary value of all orders.</td></tr><tr><td>last_order_date</td><td>Timestamp</td><td>Date of the most recent order.</td></tr><tr><td>last_shipment_status</td><td>String</td><td>Status of the most recent shipment (e.g., Delivered, In Transit).</td></tr><tr><td>rfm_segment</td><td>String</td><td>RFM-based segmentation tier (e.g., Champions, At Risk, Churned).</td></tr></tbody></table>', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, ready);

    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at, lifecycle_id) VALUES (campaign_activation_ds_id, 'audience-segments', campaign_activation_dp_id, 'Audience Segments', 'Channel-ready audience segments for targeted campaign execution', '<p><strong>Version:</strong> 1.0.0 &nbsp;|&nbsp; <strong>Freshness:</strong> Daily</p><p>This dataset transforms enriched customer segments into channel-ready audience lists for activation across email, paid media, and loyalty channels.</p>', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, draft);

    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at, lifecycle_id) VALUES (churn_model_ds_id, 'churn-scores', churn_model_dp_id, 'Churn Scores', 'Customer churn probability scores from the prediction model', '<p><strong>Version:</strong> 1.0.0 &nbsp;|&nbsp; <strong>Freshness:</strong> Daily (scored overnight)</p><p>This dataset contains probabilistic churn risk scores for each customer, produced by the churn prediction model trained on the Marketing Customer 360.</p>', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, draft);

    INSERT INTO public.role_assignments_dataset (id, dataset_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_crm_customers_ds_id, john_id, '9a9d7deb-14d9-4257-a986-7900aa70ef8f', 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.role_assignments_dataset (id, dataset_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_erp_orders_ds_id, john_id, '9a9d7deb-14d9-4257-a986-7900aa70ef8f', 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.role_assignments_dataset (id, dataset_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), logistics_wms_shipments_ds_id, john_id, '9a9d7deb-14d9-4257-a986-7900aa70ef8f', 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.role_assignments_dataset (id, dataset_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), marketing_customer_360_ds_id, alice_id, '9a9d7deb-14d9-4257-a986-7900aa70ef8f', 'APPROVED', alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    INSERT INTO public.role_assignments_dataset (id, dataset_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), campaign_activation_ds_id, alice_id, '9a9d7deb-14d9-4257-a986-7900aa70ef8f', 'APPROVED', alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    INSERT INTO public.role_assignments_dataset (id, dataset_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), churn_model_ds_id, bob_id, '9a9d7deb-14d9-4257-a986-7900aa70ef8f', 'APPROVED', bob_id, timezone('utc'::text, CURRENT_TIMESTAMP), bob_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- DATA OUTPUTS - DATASETS
    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_crm_customers_do_id, sales_crm_customers_ds_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), sales_erp_orders_do_id, sales_erp_orders_ds_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), logistics_wms_shipments_do_id, logistics_wms_shipments_ds_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), john_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), marketing_customer_360_do_id, marketing_customer_360_ds_id, 'APPROVED', alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), campaign_activation_do_id, campaign_activation_ds_id, 'APPROVED', alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), churn_model_do_id, churn_model_ds_id, 'APPROVED', bob_id, timezone('utc'::text, CURRENT_TIMESTAMP), bob_id, timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- INPUT PORTS
    -- Marketing Customer 360 consumes: Customers, Orders, Shipments
    INSERT INTO public.input_ports (id, justification, status, requested_on, approved_on, denied_on, consuming_abstract_data_product_id, dataset_id, requested_by_id, approved_by_id, denied_by_id) VALUES (gen_random_uuid(), 'Access is required to integrate Customer, Order, and Shipment data into the Marketing Customer 360. This enables RFM modeling to increase Customer Lifetime Value (LTV), improves ROAS by suppressing ads for recent purchasers, and allows for proactive retention triggers based on delivery status.', 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, marketing_customer_360_dp_id, sales_crm_customers_ds_id, alice_id, alice_id, NULL);
    INSERT INTO public.input_ports (id, justification, status, requested_on, approved_on, denied_on, consuming_abstract_data_product_id, dataset_id, requested_by_id, approved_by_id, denied_by_id) VALUES (gen_random_uuid(), 'Access is required to integrate Customer, Order, and Shipment data into the Marketing Customer 360. This enables RFM modeling to increase Customer Lifetime Value (LTV), improves ROAS by suppressing ads for recent purchasers, and allows for proactive retention triggers based on delivery status.', 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, marketing_customer_360_dp_id, sales_erp_orders_ds_id, alice_id, alice_id, NULL);
    INSERT INTO public.input_ports (id, justification, status, requested_on, approved_on, denied_on, consuming_abstract_data_product_id, dataset_id, requested_by_id, approved_by_id, denied_by_id) VALUES (gen_random_uuid(), 'Access is required to integrate Customer, Order, and Shipment data into the Marketing Customer 360. This enables RFM modeling to increase Customer Lifetime Value (LTV), improves ROAS by suppressing ads for recent purchasers, and allows for proactive retention triggers based on delivery status.', 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, marketing_customer_360_dp_id, logistics_wms_shipments_ds_id, alice_id, alice_id, NULL);
    -- Campaign Activation consumes: Customer 360
    INSERT INTO public.input_ports (id, justification, status, requested_on, approved_on, denied_on, consuming_abstract_data_product_id, dataset_id, requested_by_id, approved_by_id, denied_by_id) VALUES (gen_random_uuid(), 'Access to the Customer 360 is required to build enriched audience segments for targeted campaign activation across email, paid media, and loyalty channels.', 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, campaign_activation_dp_id, marketing_customer_360_ds_id, alice_id, alice_id, NULL);
    -- Churn Model consumes: Customer 360
    INSERT INTO public.input_ports (id, justification, status, requested_on, approved_on, denied_on, consuming_abstract_data_product_id, dataset_id, requested_by_id, approved_by_id, denied_by_id) VALUES (gen_random_uuid(), 'Access to the Customer 360 is required to train and score the churn prediction model using unified customer behavior, purchase history, and delivery data.', 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), NULL, churn_model_dp_id, marketing_customer_360_ds_id, bob_id, alice_id, NULL);

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
    INSERT INTO public.dataset_query_stats_daily (date, dataset_id, consumer_data_product_id, query_count)
    SELECT gs::date, marketing_customer_360_ds_id, campaign_activation_dp_id, 22
    FROM generate_series((CURRENT_DATE - INTERVAL '3 months')::date, CURRENT_DATE - 1, INTERVAL '1 day') AS gs
    WHERE EXTRACT(ISODOW FROM gs) BETWEEN 1 AND 5;

    INSERT INTO public.dataset_query_stats_daily (date, dataset_id, consumer_data_product_id, query_count)
    SELECT gs::date, marketing_customer_360_ds_id, churn_model_dp_id, 5
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
    -- sales_erp_orders: 06:00 UTC deadline, last refreshed 2 days ago → stale
    -- sales_crm_customers: 07:00 UTC deadline, last refreshed 2 hours ago → fresh
    -- logistics_wms_shipments: 05:00 UTC deadline, last refreshed 1 hour ago → fresh
    INSERT INTO public.output_port_freshness_slos (id, output_port_id, deadline_time, created_at, updated_at)
    VALUES
        (gen_random_uuid(), sales_erp_orders_ds_id,         '06:00:00'::time, NOW(), NOW()),
        (gen_random_uuid(), sales_crm_customers_ds_id,      '07:00:00'::time, NOW(), NOW()),
        (gen_random_uuid(), logistics_wms_shipments_ds_id,  '05:00:00'::time, NOW(), NOW());

    INSERT INTO public.output_port_freshness_observations (id, output_port_id, last_refreshed_at, created_at)
    VALUES
        (gen_random_uuid(), sales_erp_orders_ds_id,         NOW() - INTERVAL '2 days', NOW()),
        (gen_random_uuid(), sales_crm_customers_ds_id,      NOW() - INTERVAL '2 hours', NOW()),
        (gen_random_uuid(), logistics_wms_shipments_ds_id,  NOW() - INTERVAL '1 hour',  NOW());

end $$;
