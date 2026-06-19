do $$
declare
    -- DOMAINS
    customer_domain_id uuid;
    operations_and_logistics_domain_id uuid;
    financial_domain_id uuid;
    product_development_domain_id uuid;
    risk_and_compliance_domain_id uuid;
    commercial_and_customer_relationship_mgt_domain_id uuid;

    -- DATA PRODUCT TYPES
    processing_type_id uuid;
    reporting_type_id uuid;
    exploration_type_id uuid;
    ingestion_type_id uuid;
    machine_learning_type_id uuid;
    analytics_type_id uuid;

    -- USERS
    alice_id uuid;
    bob_id uuid;
    jane_id uuid;
    john_id uuid;

    -- EXPLORATIONS
    ceo_question uuid;
    coo_question uuid;

    -- DATA PRODUCTS
    data_product_lifecycle_id uuid;
    customer_segmentation_id uuid;
    customer_churn_prediction uuid;
    marketing_campaign_analysis uuid;
    customer_lifetime_value uuid;
    customer_feedback_analysis uuid;
    inventory_management uuid;
    supply_chain_optimization uuid;
    warehouse_automation_metrics uuid;
    order_fulfillment_analysis uuid;
    production_planning_insights uuid;
    revenue_dashboard uuid;
    expense_forecasting uuid;
    release_impact_analysis uuid;
    user_feedback_analysis uuid;
    data_privacy_compliance uuid;
    sales_performance_model uuid;
    cash_flow_monitoring uuid;
    fraud_detection uuid;
    financial_risk_assessment uuid;
    feature_usage_metrics uuid;
    profitability_analysis uuid;

    -- DATASETS
    production_planning_insights_forecast uuid;
    sales_performance_model_output_port uuid;
    order_fulfillment_analysis_output_port uuid;
    inventory_management_output_port uuid;
    user_feedback_insights_report uuid;
    release_impact_summary uuid;
    release_engagement_by_segment uuid;
    customer_segmentation_weekly_output_port_id uuid;
    margin_trends_by_product uuid;
    feature_usage_metrics_daily uuid;
    feature_usage_metrics_weekly uuid;
    release_version_prop_id uuid;

    -- PLATFORMS
    returned_platform_id uuid;
    azure_platform_id uuid;
    s3_service_id uuid;
    azure_blob_service_id uuid;
    glue_service_id uuid;
    returned_environment_id_dev uuid;
    returned_environment_id_prd uuid;
    azure_environment_id_dev uuid;
    azure_environment_id_prd uuid;
    databricks_id uuid;
    databricks_service_id uuid;
    snowflake_id uuid;
    snowflake_service_id uuid;
    redshift_service_id uuid;

    -- DATA OUTPUTS
    glue_configuration_id uuid;
    databricks_configuration_id uuid;
    customer_segmentation_weekly_technical_asset_id uuid;

    product_owner_id uuid;
    product_member_id uuid;
    dataset_owner_id uuid;

    -- tags
    tag_pii_id uuid;
    tag_sensitive_id uuid;
    tag_public_id uuid;
begin
    TRUNCATE TABLE public.input_ports CASCADE;
    TRUNCATE TABLE public.datasets CASCADE;
    TRUNCATE TABLE public.data_products CASCADE;
    TRUNCATE TABLE public.abstract_data_products CASCADE;
    TRUNCATE TABLE public.data_product_types CASCADE;
    TRUNCATE TABLE public.domains CASCADE;
    TRUNCATE TABLE public.tags CASCADE;
    TRUNCATE TABLE public.role_assignments_global CASCADE;
    TRUNCATE TABLE public.role_assignments_data_product CASCADE;
    TRUNCATE TABLE public.role_assignments_dataset CASCADE;
    TRUNCATE TABLE public.dataset_curated_queries CASCADE;

    -- INSERT TAGS
    INSERT INTO public.tags (id, value, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'PII', '2025-10-28 16:32:14.563446', NULL, NULL) returning id into tag_pii_id;
    INSERT INTO public.tags (id, value, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'Sensitive', '2025-10-28 16:32:27.884892', NULL, NULL) returning id into tag_sensitive_id;
    INSERT INTO public.tags (id, value, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'Public', '2025-10-28 16:32:27.884892', NULL, NULL) returning id into tag_public_id;


    -- PLATFORMS: the default configuration is added in migrations already.
    SELECT id FROM public.platforms WHERE name = 'AWS' INTO STRICT returned_platform_id;
    SELECT id FROM public.platform_services WHERE platform_id = returned_platform_id AND name = 'S3' INTO STRICT s3_service_id;
    SELECT id FROM public.platform_services WHERE platform_id = returned_platform_id AND name = 'Glue' INTO STRICT glue_service_id;
    SELECT id FROM public.platforms WHERE name = 'Azure' INTO STRICT azure_platform_id;
    SELECT id FROM public.platform_services WHERE platform_id = azure_platform_id AND name = 'azureblob' INTO STRICT azure_blob_service_id;

    -- ...existing platform configuration code...
    INSERT INTO public.platforms (id, "name") VALUES ('9be7613c-42fb-4b93-952d-1874ed1ddf77', 'Snowflake') returning id INTO snowflake_id;
    INSERT INTO public.platforms (id, "name") VALUES ('6be7613c-42fb-4b93-952d-1874ed1ddf76', 'Conveyor');
    INSERT INTO public.platform_services (id, "name", platform_id, result_string_template, technical_info_template) VALUES ('a75189c1-fa42-4980-9497-4bea4c968a5c', 'Conveyor', (SELECT id FROM public.platforms WHERE name = 'Conveyor'), '{database}.{schema}.{table}', '{database}.{schema}.{table}');
    INSERT INTO public.platform_services (id, "name", platform_id, result_string_template, technical_info_template) VALUES ('a75189c1-fa42-4980-9497-4bea4c968a5b', 'Snowflake', snowflake_id, '{database}.{schema}.{table}', '{database}.{schema}.{table}') returning id INTO snowflake_service_id;
    INSERT INTO public.platform_services (id, "name", platform_id, result_string_template, technical_info_template) VALUES ('de328223-fd90-4170-a7a1-376e4ebe0594', 'Redshift', returned_platform_id,'{database}__{schema}.{table}', '{database}__{schema}.{table}') returning id INTO redshift_service_id;
    INSERT INTO public.platforms (id, "name") VALUES ('baa5c47b-805a-4cbb-ad8b-038c66e81b7e', 'Databricks') returning id INTO databricks_id;
    INSERT INTO public.platform_services (id, "name", platform_id, result_string_template, technical_info_template) VALUES ('ce208413-b629-44d2-9f98-e5b47a315a56', 'Databricks', databricks_id, '{catalog}.{schema}.{table}', '{catalog}.{schema}.{table}') returning id INTO databricks_service_id;

    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('f4d3e8b1-5c6e-4f4a-0893-8f4e2c3d5b6a', (SELECT id FROM public.platforms WHERE name = 'Conveyor'), 'a75189c1-fa42-4980-9497-4bea4c968a5c', '["clean","master"]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('6bd82fd6-9a23-4517-a07c-9110d83ab38f', returned_platform_id, s3_service_id, '["datalake","ingress","egress"]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('fa026b3a-7a17-4c32-b279-995af021f6c2', returned_platform_id, glue_service_id, '["clean","master"]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('0b9a0e7f-8fee-4fd3-97e0-830e1612b77a', databricks_id, databricks_service_id, '["clean","master"]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('0b9a0e7f-8fee-4fd3-97e0-940e1612babc', azure_platform_id, azure_blob_service_id, '[]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('90ab1128-329f-47dd-9420-c9681bfc68c4', 'Processing', 'Data products that transform, clean, or enrich data to make it usable for other systems or analysis.', 'PROCESSING', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO processing_type_id;
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('1b4a64b3-96fb-404c-a73c-294802dc9852', 'Reporting', 'Data products that provide structured reports and dashboards for decision-making.', 'REPORTING', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO reporting_type_id;
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('74b13338-aa85-4552-8ccb-7d51550c67de', 'Exploration', 'Data products that allow users to interactively explore data for insights or discovery.', 'EXPLORATION', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO exploration_type_id;
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('c25cf2c2-418a-4d1d-a975-c6af61161546', 'Ingestion', 'Data products responsible for collecting, importing, or integrating data from various sources.', 'INGESTION', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO ingestion_type_id;
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('f1672c38-ad1a-401a-8dd3-e0b026ab1416', 'Machine Learning', 'Data products that leverage predictive models or algorithms to generate insights or predictions.', 'MACHINE_LEARNING', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO machine_learning_type_id;
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('3c289333-2d55-4aed-8bd5-85015a1567fe', 'Analytics', 'Data products that provide analysis, metrics, or aggregated insights to support business decisions.', 'ANALYTICS', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO analytics_type_id;

    -- ...existing platform service configs...
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('18e67286-92aa-449a-ba46-ac26eb0de21d', 'Solution Architect', 'data_product', 0, 'The Solution Architect for a Data Product', ARRAY [303, 309, 310, 311, 312, 313, 314], timezone('utc'::text, CURRENT_TIMESTAMP + INTERVAL '1 seconds'), NULL, NULL);
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('9ca3bfdd-2919-4190-a8bb-55e9ee7d70dd', 'Member', 'data_product', 0, 'A regular team member of a Data Product', ARRAY [313, 314, 315], timezone('utc'::text, CURRENT_TIMESTAMP + INTERVAL '2 seconds'), NULL, NULL) returning id into product_member_id;
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('2ae1b4e3-5b13-491a-912b-984e2e90b858', 'Solution Architect', 'dataset', 0, 'The Solution Architect for a Dataset', ARRAY [403, 409, 410], timezone('utc'::text, CURRENT_TIMESTAMP + INTERVAL '1 seconds'), NULL, NULL);
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('db8d7a76-c50b-4e95-8549-8da86f48e7c2', 'Member', 'dataset', 0, 'A regular team member of a Dataset', ARRAY [413], timezone('utc'::text, CURRENT_TIMESTAMP + INTERVAL '2 seconds'), NULL, NULL);

    SELECT id FROM public.roles WHERE scope = 'data_product' AND prototype = 2 INTO STRICT product_owner_id;
    SELECT id FROM public.roles WHERE scope = 'dataset' AND prototype = 2 INTO STRICT dataset_owner_id;

    -- ENVIRONMENTS
    INSERT INTO public.environments ("name", context, acronym, is_default, created_on, updated_on, deleted_at) VALUES ('development', 'arn:aws:iam::{{ AWS_ACCOUNT_ID }}:role/{{ AWS_ROLE_WITH_CONTEXT_TEMPLATE_DEV }}', 'dev', true, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO returned_environment_id_dev;
    INSERT INTO public.environments ("name", context, acronym, is_default, created_on, updated_on, deleted_at) VALUES ('production', 'arn:aws:iam::{{ AWS_ACCOUNT_ID }}:role/{{ AWS_ROLE_WITH_CONTEXT_TEMPLATE_PRD }}', 'prd', false, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO returned_environment_id_prd;
    INSERT INTO public.environments ("name", context, acronym, is_default, created_on, updated_on, deleted_at) VALUES ('azure_development', '', 'azure_dev', true, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO azure_environment_id_dev;
    INSERT INTO public.environments ("name", context, acronym, is_default, created_on, updated_on, deleted_at) VALUES ('azure_production', '', 'azure_prd', false, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO azure_environment_id_prd;


    INSERT INTO public.env_platform_configs (id, environment_id, platform_id, "config", created_on, updated_on, deleted_at) VALUES ('daa8e3e8-1485-4eb2-8b4b-575e8d10a570', returned_environment_id_dev, returned_platform_id, '{"account_id": "{{ AWS_ACCOUNT_ID }}", "region": "{{ AWS_REGION }}", "can_read_from": ["production"]}', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_configs (id, environment_id, platform_id, "config", created_on, updated_on, deleted_at) VALUES ('e2aa2f6d-585f-4b43-8ea4-982b7bab0142', returned_environment_id_prd, returned_platform_id, '{"account_id": "{{ AWS_ACCOUNT_ID }}", "region": "{{ AWS_REGION }}", "can_read_from": []}', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_configs (id, environment_id, platform_id, "config", created_on, updated_on, deleted_at) VALUES ('5288e3e8-5885-4eb2-964b-575e8d105689', azure_environment_id_dev, azure_platform_id, '{"tenant_id": "{{ AZURE_TENANT_ID }}", "region": "{{ AZURE_REGION }}", "subscription_id": "{{ AZURE_SUBSCRIPTION_ID }}", "can_read_from": ["production"]}', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_configs (id, environment_id, platform_id, "config", created_on, updated_on, deleted_at) VALUES ('cd892f6d-585f-9843-aba4-982b7bab0523', azure_environment_id_prd, azure_platform_id, '{"tenant_id": "{{ AZURE_TENANT_ID }}", "region": "{{ AZURE_REGION }}", "subscription_id": "{{ AZURE_SUBSCRIPTION_ID }}", "can_read_from": []}', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('93f4b677-5ae8-450d-91a6-e15196b2e774', returned_environment_id_dev, returned_platform_id, s3_service_id, '[{"identifier":"datalake","bucket_name":"{{ DATALAKE_BUCKET_NAME_DEV }}","bucket_arn":"{{ DATALAKE_BUCKET_ARN_DEV }}","kms_key_arn":"{{ DATALAKE_BUCKET_KMS_ARN_DEV }}","is_default":true},{"identifier":"ingress","bucket_name":"{{ INGRESS_BUCKET_NAME_DEV }}","bucket_arn":"{{ INGRESS_BUCKET_ARN_DEV }}","kms_key_arn":"{{ INGRESS_BUCKET_KMS_ARN_DEV }}","is_default":false},{"identifier":"egress","bucket_name":"{{ EGRESS_BUCKET_NAME_DEV }}","bucket_arn":"{{ EGRESS_BUCKET_ARN_DEV }}","kms_key_arn":"{{ EGRESS_BUCKET_KMS_ARN_DEV }}","is_default":false}]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('9c1d025c-f342-4665-8461-ba8b9f4035ff', returned_environment_id_prd, returned_platform_id, s3_service_id, '[{"identifier":"datalake","bucket_name":"{{ DATALAKE_BUCKET_NAME_PRD }}","bucket_arn":"{{ DATALAKE_BUCKET_ARN_PRD }}","kms_key_arn":"{{ DATALAKE_BUCKET_KMS_ARN_PRD }}","is_default":true},{"identifier":"ingress","bucket_name":"{{ INGRESS_BUCKET_NAME_PRD }}","bucket_arn":"{{ INGRESS_BUCKET_ARN_PRD }}","kms_key_arn":"{{ INGRESS_BUCKET_KMS_ARN_PRD }}","is_default":false},{"identifier":"egress","bucket_name":"{{ EGRESS_BUCKET_NAME_PRD }}","bucket_arn":"{{ EGRESS_BUCKET_ARN_PRD }}","kms_key_arn":"{{ EGRESS_BUCKET_KMS_ARN_PRD }}","is_default":false}]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('6afd025c-f342-5286-8461-ba8b9f4039dc', azure_environment_id_prd, azure_platform_id, azure_blob_service_id, '[{"identifier":"azure_prd","storage_account_names": { "default": "defaultartifactsprd"}}]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('8dc4b677-5ae8-7823-91a6-e15196b2e562', azure_environment_id_dev, azure_platform_id, azure_blob_service_id, '[{"identifier":"azure_dev","storage_account_names": {"default": "defaultartifactsdev"}}]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('1c52b0e5-961f-412a-995e-0c1efae19f41', returned_environment_id_dev, returned_platform_id, glue_service_id, '[{"identifier":"clean_test","database_name":"clean_test_dev","bucket_identifier":"datalake","s3_path":"clean/test"},{"identifier":"master_test","database_name":"master_test_dev","bucket_identifier":"datalake","s3_path":"master/test"}]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('ba42ca59-ab5d-498e-8cd0-cdd680f80bb0', returned_environment_id_prd, returned_platform_id, glue_service_id, '[{"identifier":"clean_test","database_name":"clean_test_prd","bucket_identifier":"datalake","s3_path":"clean/test"},{"identifier":"master_test","database_name":"master_test_prd","bucket_identifier":"datalake","s3_path":"master/test"}]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- DOMAINS
    INSERT INTO public.domains (id, name, description, created_on, updated_on, deleted_at) VALUES ('672debaf-31f9-4233-820b-ad2165af044e', 'Customer Insights', 'Contains data products that provide information about customer behavior, demographics and satisfaction.', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO customer_domain_id;
    INSERT INTO public.domains (id, name, description, created_on, updated_on, deleted_at) VALUES ('bd09093e-14ff-41c1-b74d-7c2ce9821d1c', 'Operations & Logistics', 'Data products that track internal operations, supply chain efficiency and resource utilization.', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO operations_and_logistics_domain_id;
    INSERT INTO public.domains (id, name, description, created_on, updated_on, deleted_at) VALUES ('8798B58A-9119-43D1-9365-DC83E07B8D87', 'Financial Performance', 'Data products focused on revenue, expenses, profitability and other financial metrics.', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO financial_domain_id;
    INSERT INTO public.domains (id, name, description, created_on, updated_on, deleted_at) VALUES ('623e6fbf-3a06-434e-995c-b0336e71806e', 'Product Development', 'Data products that capture product usage, feature adoption and performance metrics.', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO product_development_domain_id;
    INSERT INTO public.domains (id, name, description, created_on, updated_on, deleted_at) VALUES ('bec196cb-81df-4cfc-959f-b142c312861e', 'Risk & Compliance', 'Data products designed to monitor regulatory compliance, security and operational risks', '2025-10-28 16:30:24.123498', NULL, NULL) returning id  INTO risk_and_compliance_domain_id;
    INSERT INTO public.domains (id, name, description, created_on, updated_on, deleted_at) VALUES ('acaaaafe-cde9-4746-9835-f1e0c3c85b6c', 'Commercial and Customer Relationship Management', 'Commercial and CRM', '2025-10-28 16:30:41.743083', NULL, NULL) returning id into commercial_and_customer_relationship_mgt_domain_id;

    -- DATA PRODUCT TYPES
    -- ...existing data product types code...

    -- USERS
    INSERT INTO public.users (email, id, external_id, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('alice.baker@pharma.com', 'a02d3714-97e3-40d8-92b7-3b018fd1229f', 'alice.baker@pharma.com', 'Alice', 'Baker', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO alice_id;
    INSERT INTO public.users (email, id, external_id, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('bob.johnson@pharma.com', '35f2dd11-3119-4eb3-8f19-01b323131221', 'bob.johnson@pharma.com', 'Bob', 'Johnson', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO bob_id;
    INSERT INTO public.users (email, id, external_id, can_become_admin, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('jane.researcher@pharma.com', 'd9f3aae2-391e-46c1-aec6-a7ae1114a7da', 'jane.researcher@pharma.com', true, 'Jane', 'Researcher', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO jane_id;
    INSERT INTO public.users (email, id, external_id, can_become_admin, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('john.scientist@pharma.com', 'b72fca38-17ff-4259-a075-5aaa5973343c', 'john.scientist@pharma.com', true, 'John', 'Scientist', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO john_id;

    -- ROLES
    -- ...existing roles code...

    SELECT '00000000-0000-0000-0000-000000000001' INTO data_product_lifecycle_id;
    INSERT INTO data_product_lifecycles (id, name, value, color, is_default) SELECT data_product_lifecycle_id, 'Draft', 0, 'grey', true WHERE NOT EXISTS (SELECT 1 FROM public.data_product_lifecycles WHERE id = data_product_lifecycle_id);

    -- Customer segmentation id
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'active', '{}', 'Customer Segmentation', 'customer_segmentation', 'data_products', 'Groups customers based on demographics, behavior, and purchase patterns.', customer_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into customer_segmentation_id;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (customer_segmentation_id, '<h2>Customer Segmentation</h2><p></p><p>This data product aims to provide a centralized view of customer segments across demographics and behavior.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Enable targeted marketing and product strategies</li><li>Identify high-value customer groups</li><li>Support personalized engagement campaigns</li></ul>', '3c289333-2d55-4aed-8bd5-85015a1567fe', NULL, NULL);
    INSERT INTO public.tags_data_products (data_product_id, tag_id) VALUES (customer_segmentation_id, tag_sensitive_id);

    -- Customer segementation id -- Customer segments weekly
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'customer_segments_weekly', customer_segmentation_id, 'Customer Segments Weekly', 'Weekly segmentation of customers by demographics and purchase behavior', 'Provides the latest segmentation of customers to guide marketing and targeting. Key objectives: - Identify high-value segments - Support campaign personalization - Update targeting weekly', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into customer_segmentation_weekly_output_port_id;
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES (gen_random_uuid(), 'customer-segments-weekly-table', 'Customer segments weekly s3 table', 'Weekly segmentation of customers by demographics and purchase behavior', 'ACTIVE', returned_platform_id, glue_service_id, customer_segmentation_id, NULL, '12346cc6-f58d-4217-88d3-6443b01d5d0f', '2025-10-28 16:34:02.355842', NULL, NULL, 'default') returning id into customer_segmentation_weekly_technical_asset_id;
    INSERT INTO public.tags_data_outputs (data_output_id, tag_id, created_on, updated_on) VALUES (customer_segmentation_weekly_technical_asset_id, tag_pii_id, '2025-10-28 17:56:57.829806', NULL);
    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), customer_segmentation_weekly_technical_asset_id, customer_segmentation_weekly_output_port_id, 'APPROVED', john_id, '2025-10-28 16:36:36.784134', john_id, '2025-10-28 16:36:36.936773', NULL, NULL, '2025-10-28 16:36:36.677803', '2025-10-28 16:36:36.838041', NULL);
    INSERT INTO public.tags_datasets (dataset_id, tag_id) VALUES (customer_segmentation_weekly_output_port_id, tag_sensitive_id);


    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('eb8bb332-b05e-4529-af43-90f69a6a90bb', 'customer_segments_monthly', customer_segmentation_id, 'Customer Segments Monthly', 'Monthly aggregated customer segments', 'Provides monthly view of customer groups for strategic planning. Key objectives: - Track segment evolution - Support executive reporting - Feed into predictive models', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- Customer churn prediction
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('0a883317-d6c0-44e1-93b2-ba531fa9eeab', 'active', '{}', 'Customer Churn Prediction', 'customer_churn_prediction', 'data_products', 'Predicts which customers are likely to leave using historical data.', customer_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into customer_churn_prediction;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (customer_churn_prediction, '<h2>Customer Churn Prediction</h2><p></p><p>This data product aims to anticipate customer attrition using predictive modeling.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Proactively engage at-risk customers</li><li>Reduce churn rates</li><li>Optimize retention strategies</li></ul>', 'f1672c38-ad1a-401a-8dd3-e0b026ab1416', NULL, NULL);
    INSERT INTO public.tags_data_products (data_product_id, tag_id) VALUES (customer_churn_prediction, tag_public_id);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('208cc524-5df2-47dd-b8b7-489ad2c5553a', 'weekly_churn_probabilities', customer_churn_prediction, 'Weekly Churn Probabilities', 'Predicted churn probability per customer, updated weekly', 'Provides actionable insights for retention campaigns. Key objectives: - Enable timely interventions - Support sales and marketing - Reduce churn', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('f3aa47cf-81cc-4bc8-9876-1960b8ddcd6c', 'monthly_churn_targets', customer_churn_prediction, 'Monthly Churn Targets', 'Aggregated churn targets for marketing campaigns', 'Provides monthly churn-focused marketing guidance. Key objectives: - Plan anti-churn campaigns - Measure campaign effectiveness - Prioritize high-risk customers', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- Marketing campaign analysis
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('403d19c9-2056-4fb7-b820-d163df800e8f', 'active', '{}', 'Marketing Campaign Analysis', 'marketing_campaign_analysis', 'data_products', 'Evaluates the performance of marketing campaigns across channels.', customer_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into marketing_campaign_analysis;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (marketing_campaign_analysis, '<h2>Marketing Campaign Analysis</h2><p></p><p>This data product provides insights into marketing campaign effectiveness.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Measure ROI of campaigns</li><li>Identify best-performing channels</li><li>Support marketing optimization</li></ul>', '1b4a64b3-96fb-404c-a73c-294802dc9852', NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('0deeb253-7b8c-4ece-8a9c-29524bbc5c00', 'campaign_performance_summary', marketing_campaign_analysis, 'Campaign Performance Summary', 'KPIs for each marketing campaign', 'Provides campaign results to optimize channel strategy and improve customer retention. Key objectives: - Track ROI - Identify best-performing campaigns - Inform budget allocation', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('7372d7e7-aee3-4644-8ee2-237af4d0899e', 'ad_spend_vs_roi', marketing_campaign_analysis, 'Ad Spend Vs Roi', 'Comparison of spend vs campaign results', 'Measures effectiveness of marketing investments. Key objectives: - Optimize marketing spend - Support executive reporting - Improve ROI', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('b68f13d1-b9e8-4e27-96fa-9d6f029614c6', 'top_engaged_segments', marketing_campaign_analysis, 'Top Engaged Segments', 'Identifies most engaged customer segments per campaign', 'Combines marketing and customer segmentation data to target communications. Key objectives: - Focus campaigns on high-engagement segments - Improve conversions - Optimize messaging', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- Customer lifetime value
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('9a78d3cc-0c0d-4d0b-a314-aeb99c8cecf3', 'active', '{}', 'Customer Lifetime Value', 'customer_lifetime_value', 'data_products', 'Calculates expected revenue per customer over their relationship.', customer_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into customer_lifetime_value;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (customer_lifetime_value, '<h2>Customer Lifetime Value</h2><p></p><p>This data product estimates customer lifetime value to guide business decisions.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Prioritize high-value customers</li><li>Optimize marketing spend</li><li>Inform loyalty programs</li></ul>', '3c289333-2d55-4aed-8bd5-85015a1567fe', NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('22b583ce-d052-49b3-98c9-92483282f303', 'customer_lifetime_value_scores', customer_lifetime_value, 'Customer Lifetime Value Scores', 'Predicted lifetime value per customer', 'Provides metrics to prioritize high-value customers. Key objectives: - Guide marketing spend - Support sales strategy - Inform loyalty programs', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);


    -- Customer feedback analysis
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('66563731-1be2-493c-b692-aef4cc29e493', 'active', '{}', 'Customer Feedback Analysis', 'customer_feedback_analysis', 'data_products', 'Analyzes surveys and reviews to understand satisfaction and needs.', customer_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into customer_feedback_analysis;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (customer_feedback_analysis, '<h2>Customer Feedback Analysis</h2><p></p><p>This data product centralizes customer feedback analysis for actionable insights.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Understand customer satisfaction</li><li>Identify improvement areas</li><li>Support product and service enhancements</li></ul>', '74b13338-aa85-4552-8ccb-7d51550c67de', NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('67ae0fa8-5e88-4712-b5a1-5a9fc423131f', 'customer_feedback_summary', customer_feedback_analysis, 'Customer Feedback Summary', 'Summary of feedback trends from surveys and reviews', 'Provides insights into customer sentiment and satisfaction. Key objectives: - Identify pain points - Prioritize product improvements - Track satisfaction over time', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('e2a641fc-c9ef-40a2-98be-76a7585db5d6', 'feature_feedback_ranking', customer_feedback_analysis, 'Feature Feedback Ranking', 'Ranked insights about product features from user feedback', 'Combines usage metrics with feedback to understand feature impact. Key objectives: - Highlight areas for product improvement - Guide roadmap prioritization - Support UX decisions', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- Inventory management
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('65254a60-6f97-4b6c-812c-84dcf7c316e3', 'active', '{}', 'Inventory Management', 'inventory_management', 'data_products', 'Tracks stock levels, turnover, and replenishment schedules.', operations_and_logistics_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into inventory_management;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (inventory_management, '<h2>Inventory Management</h2><p></p><p>This data product provides a centralized platform for managing inventory efficiently.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Monitor stock levels in real-time</li><li>Reduce stockouts and overstock</li><li>Improve warehouse operations</li></ul>', '1b4a64b3-96fb-404c-a73c-294802dc9852', NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('aa84c8a8-9ca3-47be-9389-c75458e326a2', 'inventory_status', '65254a60-6f97-4b6c-812c-84dcf7c316e3', 'Inventory Status', 'Current stock levels per warehouse', 'Provides visibility into inventory to prevent stockouts or overstock. Key objectives: - Monitor stock levels - Support replenishment planning - Reduce costs', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into inventory_management_output_port;

    -- Supply chain optimization
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('429f80cf-bce9-4ac5-bafc-0c153df466fc', 'active', '{}', 'Supply Chain Optimization', 'supply_chain_optimization', 'data_products', 'Analyzes supplier performance, delivery times, and transportation costs.', operations_and_logistics_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into supply_chain_optimization;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (supply_chain_optimization, '<h2>Supply Chain Optimization</h2><p></p><p>This data product aims to optimize supply chain efficiency across operations.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Track supplier performance</li><li>Reduce delivery delays</li><li>Minimize transportation costs</li></ul>', '3c289333-2d55-4aed-8bd5-85015a1567fe', NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('5891bb7a-ed88-4ba1-8826-7c143243f91f', 'supplier_performance_report', supply_chain_optimization, 'Supplier Performance Report', 'Supplier KPIs including delivery times and reliability', 'Provides insights to optimize supply chain efficiency. Key objectives: - Track supplier reliability - Identify delays - Improve procurement', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- Warehouse automation metrics
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('867e3ad0-7a11-4687-bd39-3e41ad9f2ed0', 'active', '{}', 'Warehouse Automation Metrics', 'warehouse_automation_metrics', 'data_products', 'Monitors efficiency of warehouse processes using sensor and IoT data.', operations_and_logistics_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into warehouse_automation_metrics;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (warehouse_automation_metrics, '<h2>Warehouse Automation Metrics</h2><p></p><p>This data product centralizes warehouse automation metrics for operational improvement.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Track process efficiency</li><li>Identify bottlenecks</li><li>Support automation initiatives</li></ul>', 'f1672c38-ad1a-401a-8dd3-e0b026ab1416', NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('05ae0792-f70a-422c-abc1-16fd8c9348bb', 'warehouse_efficiency_metrics', warehouse_automation_metrics, 'Warehouse Efficiency Metrics', 'KPIs from automated warehouse operations', 'Provides data to improve operational efficiency. Key objectives: - Identify bottlenecks - Measure automation impact - Support resource allocation', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('4c4ff241-9885-48eb-8b2a-b1a1d66092a3', 'automated_pick_pack_rates', warehouse_automation_metrics, 'Automated Pick Pack Rates', 'Metrics for automated picking and packing', 'Provides detailed operational data for efficiency optimization. Key objectives: - Track speed and accuracy - Support automation planning - Reduce operational costs', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    --Order fulfillment analysis
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('c9940b6c-b0be-48d4-a546-cab8afa6cf4b', 'active', '{}', 'Order Fulfillment Analysis', 'order_fulfillment_analysis', 'data_products', 'Tracks order processing time and delivery success rates.', operations_and_logistics_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into order_fulfillment_analysis;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (order_fulfillment_analysis, '<h2>Order Fulfillment Analysis</h2><p></p><p>This data product provides visibility into order fulfillment performance.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Monitor processing times</li><li>Improve delivery success rates</li><li>Enhance customer satisfaction</li></ul>', '3c289333-2d55-4aed-8bd5-85015a1567fe', NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('b928519b-21f9-4877-975b-686c2b336522', 'order_fulfillment_stats', order_fulfillment_analysis, 'Order Fulfillment Stats', 'Metrics on order processing and delivery success', 'Provides visibility into fulfillment performance. Key objectives: - Track delivery efficiency - Improve customer satisfaction - Reduce delays', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into order_fulfillment_analysis_output_port;
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('5d99a121-826d-4426-be8a-bc820b5be365', 'delayed_orders_report', order_fulfillment_analysis, 'Delayed Orders Report', 'Orders delayed beyond SLA', 'Identifies bottlenecks in fulfillment. Key objectives: - Highlight issues - Support logistics improvements - Inform customer communication', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- Production planning insights
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('c550880e-fcc8-4048-a6ce-fec8903b5521', 'active', '{}', 'Production Planning Insights', 'production_planning_insights', 'data_products', 'Predicts production needs and schedules resources effectively.', operations_and_logistics_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into production_planning_insights;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (production_planning_insights, '<h2>Production Planning Insights</h2><p></p><p>This data product centralizes production planning insights to optimize operations.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Forecast production requirements</li><li>Allocate resources efficiently</li><li>Reduce downtime</li></ul>', '3c289333-2d55-4aed-8bd5-85015a1567fe', NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('821b84ce-a702-44f7-8521-971954c0a208', 'production_planning_forecast', production_planning_insights, 'Production Planning Forecast', 'Forecast of production requirements', 'Provides projections to optimize scheduling and capacity. Key objectives: - Reduce downtime - Optimize resource allocation - Support operational planning', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into production_planning_insights_forecast;
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('bc7b3d51-1941-4312-ba83-4594c331cf05', 'production_variance_report', production_planning_insights, 'Production Variance Report', 'Difference between planned and actual production', 'Provides insights into production deviations. Key objectives: - Identify inefficiencies - Improve planning accuracy - Support operations', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- Sales performance model
    INSERT INTO public.abstract_data_products (id, status, finalizers, name, namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('86b74246-734f-4cea-a984-3dd0d27fc565', 'active', '{}', 'Sales performance model', 'sales-performance-model', 'data_products', 'Evaluates sales productivity and regional performance.
    It enables resource re-allocation and forecasting improvements.', commercial_and_customer_relationship_mgt_domain_id, '2025-10-28 18:19:20.450469', NULL, NULL) returning id into sales_performance_model;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (sales_performance_model, NULL, '90ab1128-329f-47dd-9420-c9681bfc68c4', data_product_lifecycle_id, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'sales_performance', sales_performance_model, 'Sales performance', 'Sales performance data', 'Provides an overview of sales performance data', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into sales_performance_model_output_port;
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('93556532-e5e5-4c8a-b0f6-e269a9e290cd', 'sales-transactions', 'Sales Transactions', 'Stores product-level revenue and quantity sold per region', 'ACTIVE', returned_platform_id, glue_service_id, sales_performance_model, NULL, 'ff632a7d-4ddd-4fd1-800a-ba8098c26c18', '2025-10-28 18:19:44.674412', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('2845c506-a944-484e-a9b5-3f93d9f1532c', 'territory-assignments', 'Territory Assignments', 'Defines which representatives cover which areas or accounts.', 'ACTIVE', returned_platform_id, glue_service_id, sales_performance_model, NULL, 'e8129149-bdb5-4c15-8211-4b6b83fcb64a', '2025-10-28 18:20:01.401722', NULL, NULL, 'default');

    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), '93556532-e5e5-4c8a-b0f6-e269a9e290cd', sales_performance_model_output_port, 'APPROVED', john_id, '2025-10-28 16:36:36.784134', john_id, '2025-10-28 16:36:36.936773', NULL, NULL, '2025-10-28 16:36:36.677803', '2025-10-28 16:36:36.838041', NULL);
    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), '2845c506-a944-484e-a9b5-3f93d9f1532c', sales_performance_model_output_port, 'APPROVED', john_id, '2025-10-28 16:36:36.784134', john_id, '2025-10-28 16:36:36.936773', NULL, NULL, '2025-10-28 16:36:36.677803', '2025-10-28 16:36:36.838041', NULL);

    -- Revenue dashboard
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('b976c1af-2199-420b-8e70-76b7ea4119ad', 'active', '{}', 'Revenue Dashboard', 'revenue_dashboard', 'data_products', 'Tracks revenue by product line, region, and period.', financial_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into revenue_dashboard;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (revenue_dashboard, '<h2>Revenue Dashboard</h2><p></p><p>This data product provides a consolidated view of company revenue.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Monitor revenue trends</li><li>Identify growth opportunities</li><li>Support strategic decision-making</li></ul>', '1b4a64b3-96fb-404c-a73c-294802dc9852', NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('b076bf53-463a-47bb-84a9-596d45b425d7', 'revenue_dashboard_summary', revenue_dashboard, 'Revenue Dashboard Summary', 'Consolidated revenue metrics', 'Provides a single view of revenue trends. Key objectives: - Track revenue by product and region - Identify growth opportunities - Support executive reporting', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('393cf08a-d05c-442a-8982-d7d2cced4ad2', 'revenue_by_segment', revenue_dashboard, 'Revenue By Segment', 'Revenue broken down by customer segments', 'Enables analysis of profitability per segment. Key objectives: - Inform marketing targeting - Support strategic planning - Monitor high-value customers', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);


    -- Revenue dashboard - input ports
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
        VALUES (gen_random_uuid(),'Needed to predict our revenue', revenue_dashboard, production_planning_insights_forecast, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
        VALUES (gen_random_uuid(),'Needed to predict our revenue', revenue_dashboard, sales_performance_model_output_port, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
        VALUES (gen_random_uuid(),'Needed to predict our revenue', revenue_dashboard, order_fulfillment_analysis_output_port, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
        VALUES (gen_random_uuid(),'Needed to predict our revenue', revenue_dashboard, inventory_management_output_port, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);


    -- Expense forecasting
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'active', '{}', 'Expense Forecasting', 'expense_forecasting', 'data_products', 'Predicts future expenses using historical financial data.', financial_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into expense_forecasting;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (expense_forecasting, '<h2>Expense Forecasting</h2><p></p><p>This data product enables proactive expense management through forecasting.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Anticipate future costs</li><li>Support budgeting and planning</li><li>Reduce financial risk</li></ul>', 'f1672c38-ad1a-401a-8dd3-e0b026ab1416', NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('d4e7792b-fb93-4541-beb9-b3c2b2474c77', 'expense_forecast', expense_forecasting, 'Expense Forecast', 'Predicted expenses by category', 'Provides insight into expected costs to support budgeting. Key objectives: - Forecast future expenses - Support planning - Reduce financial risk', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- Expense forecasting input ports
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
        VALUES ('0658e52e-b69e-4787-b7b1-df215d75329c','Needed to predict our expenses, production planning is an important dataset', expense_forecasting, production_planning_insights_forecast, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- User feedback analysis
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'active', '{}', 'User Feedback Analysis', 'user_feedback_analysis', 'data_products', 'Uses text mining to extract insights from user reviews and surveys.', product_development_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into user_feedback_analysis;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (user_feedback_analysis, '<h2>User Feedback Analysis</h2><p></p><p>This data product enables centralized analysis of user feedback for product improvement.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Extract insights from reviews and surveys</li><li>Identify pain points</li><li>Inform UX and feature decisions</li></ul>', 'f1672c38-ad1a-401a-8dd3-e0b026ab1416', NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('9cfcdd85-8049-42fc-8984-6a6fc7bfeba9', 'feedback_insights_report', user_feedback_analysis, 'Feedback Insights Report', 'Summarized insights from user feedback', 'Provides actionable insights for product improvements. Key objectives: - Identify pain points - Prioritize changes - Improve satisfaction', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into user_feedback_insights_report;

    -- Release impact analysis
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'active', '{}', 'Release Impact Analysis', 'release_impact_analysis', 'data_products', 'Measures effect of new releases on usage and performance.', product_development_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into release_impact_analysis;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (release_impact_analysis, '<h2>Release Impact Analysis</h2><p></p><p>This data product centralizes insights on release impact for better planning.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Assess adoption of new features</li><li>Measure performance impact</li><li>Guide future release planning</li></ul>', '3c289333-2d55-4aed-8bd5-85015a1567fe', NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('e3dfeb4e-e7ee-4db2-84ce-7f4f36840c96', 'release_engagement_by_segment', release_impact_analysis, 'Release Engagement By Segment', 'Feature adoption per customer segment', 'Helps measure differential impact of releases across user groups. Key objectives: - Understand segment behavior - Inform targeted communications - Optimize rollout', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into release_engagement_by_segment;
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('56acafd4-5bb8-45b1-81fa-acfab84ec3fc', 'release_impact_summary', release_impact_analysis, 'Release Impact Summary', 'Metrics on usage changes after new releases', 'Provides insight into feature release performance. Key objectives: - Measure adoption - Detect regressions - Inform next releases', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into release_impact_summary;

    -- Data privacy compliance
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'active', '{}', 'Data Privacy Compliance', 'data_privacy_compliance', 'data_products', 'Monitors adherence to GDPR and other privacy regulations.', risk_and_compliance_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into data_privacy_compliance;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (data_privacy_compliance, '<h2>Data Privacy Compliance</h2><p></p><p>This data product ensures compliance with data privacy regulations.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Monitor GDPR compliance</li><li>Identify gaps in privacy practices</li><li>Support regulatory reporting</li></ul>', '1b4a64b3-96fb-404c-a73c-294802dc9852', NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('e94890c6-0da8-4a1e-b696-e53e5312f743', 'privacy_compliance_report', data_privacy_compliance, 'Privacy Compliance Report', 'GDPR and privacy compliance metrics', 'Provides compliance tracking for regulatory adherence. Key objectives: - Identify gaps - Support audits - Ensure legal compliance', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- Data privacy compliance - input ports
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
        VALUES (gen_random_uuid(),'Needed to check for GDPR compliance', data_privacy_compliance, user_feedback_insights_report, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
        VALUES (gen_random_uuid(),'Needed to check for GDPR compliance', data_privacy_compliance, release_engagement_by_segment, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
        VALUES (gen_random_uuid(),'Needed to check for GDPR compliance', data_privacy_compliance, release_impact_summary, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
        VALUES (gen_random_uuid(),'Needed to check for GDPR compliance', data_privacy_compliance, customer_segmentation_weekly_output_port_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);


    -- Cash flow monitoring
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'active', '{}', 'Cash Flow Monitoring', 'cash_flow_monitoring', 'data_products', 'Monitors inflows and outflows of funds in real-time.', financial_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into cash_flow_monitoring;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (cash_flow_monitoring, '<h2>Cash Flow Monitoring</h2><p></p><p>This data product provides real-time cash flow monitoring for financial stability.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Track daily cash movements</li><li>Ensure liquidity and solvency</li><li>Support financial decision-making</li></ul>', '1b4a64b3-96fb-404c-a73c-294802dc9852', NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('dcb24163-bfec-44d8-b025-1d656d0fff36', 'cash_flow_overview', cash_flow_monitoring, 'Cash Flow Overview', 'Daily inflows and outflows', 'Provides real-time view of cash position. Key objectives: - Ensure liquidity - Identify gaps - Support financial planning', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- Cash flow monitoring - input ports
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
    VALUES (gen_random_uuid(),'Needed for cash flow monitoring', cash_flow_monitoring, sales_performance_model_output_port, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
    VALUES (gen_random_uuid(),'Needed for cash flow monitoring', cash_flow_monitoring, inventory_management_output_port, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- Fraud detection
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'active', '{}', 'Fraud Detection', 'fraud_detection', 'data_products', 'Detects suspicious activities in transactions using historical patterns.', risk_and_compliance_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into fraud_detection;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (fraud_detection, '<h2>Fraud Detection</h2><p></p><p>This data product centralizes fraud detection insights for risk mitigation.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Identify suspicious transactions</li><li>Prevent financial losses</li><li>Support security investigations</li></ul>', 'f1672c38-ad1a-401a-8dd3-e0b026ab1416', NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'fraud_detection_alerts', fraud_detection, 'Fraud Detection Alerts', 'Transactions flagged for potential fraud', 'Provides actionable fraud detection results. Key objectives: - Prevent losses - Investigate suspicious activity - Improve security', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- Fraud detection - input ports
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
    VALUES (gen_random_uuid(),'Needed for fraud detection', fraud_detection, sales_performance_model_output_port, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
    VALUES (gen_random_uuid(),'Needed for fraud detection', fraud_detection, inventory_management_output_port, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- Profitability analysis
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'active', '{}', 'Profitability Analysis', 'profitability_analysis', 'data_products', 'Identifies which products or services contribute most to profit.', financial_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into profitability_analysis;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (profitability_analysis, '<h2>Profitability Analysis</h2><p></p><p>This data product centralizes profitability insights to guide business strategy.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Identify high-margin products</li><li>Optimize product portfolio</li><li>Inform investment decisions</li></ul>', '3c289333-2d55-4aed-8bd5-85015a1567fe', NULL, NULL);

    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'profitability_analysis_report', profitability_analysis, 'Profitability Analysis Report', 'Product and service profit contribution', 'Provides insight into profitability for portfolio decisions. Key objectives: - Identify high-margin offerings - Guide investment strategy - Support executive decisions', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'margin_trends_by_product', profitability_analysis, 'Margin Trends By Product', 'Historical margin trends per product', 'Provides deeper understanding of profitability over time. Key objectives: - Detect declining margins - Inform pricing strategies - Support product decisions', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into margin_trends_by_product;

    -- Financial risk assessment
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'active', '{}', 'Financial Risk Assessment', 'financial_risk_assessment', 'data_products', 'Evaluates potential financial risks and exposure.', financial_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into financial_risk_assessment;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (financial_risk_assessment, '<h2>Financial Risk Assessment</h2><p></p><p>This data product centralizes financial risk evaluation for proactive management.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Identify financial risks</li><li>Support compliance and regulatory requirements</li><li>Guide investment decisions</li></ul>', '3c289333-2d55-4aed-8bd5-85015a1567fe', NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'financial_risk_dashboard', financial_risk_assessment, 'Financial Risk Dashboard', 'Metrics highlighting financial exposure', 'Provides risk analysis to prevent losses. Key objectives: - Track financial risks - Support mitigation strategies - Enable compliance', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

     -- Financial risk - input ports
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
    VALUES (gen_random_uuid(),'Needed for detecting financial risks', financial_risk_assessment, sales_performance_model_output_port, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
    VALUES (gen_random_uuid(),'Needed for detecting financial risks', financial_risk_assessment, inventory_management_output_port, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
    VALUES (gen_random_uuid(),'Needed for detecting financial risks', financial_risk_assessment, margin_trends_by_product, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);


    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(), 'active', '{}', 'Feature Usage Metrics', 'feature_usage_metrics', 'data_products', 'Tracks how often users engage with product features.', product_development_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into feature_usage_metrics;
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES (feature_usage_metrics, '<h2>Feature Usage Metrics</h2><p></p><p>This data product provides a centralized view of feature adoption and usage.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Monitor user engagement</li><li>Identify popular features</li><li>Inform product development priorities</li></ul>', '1b4a64b3-96fb-404c-a73c-294802dc9852', NULL, NULL);

    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('b8f56c2f-da55-4be5-9625-ba2a4e4a42c2', 'daily_feature_engagement', feature_usage_metrics, 'Daily Feature Engagement', 'Daily usage metrics per feature', 'Provides insights into feature adoption. Key objectives: - Monitor engagement - Guide product improvements - Track trends', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into feature_usage_metrics_daily;
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('f3a95935-5a3e-4427-be75-a01a40a53f55', 'weekly_feature_summary', feature_usage_metrics, 'Weekly Feature Summary', 'Aggregated weekly feature usage', 'Provides weekly trends for product teams. Key objectives: - Identify adoption patterns - Support roadmap planning - Enable executive reporting', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL)returning id into feature_usage_metrics_weekly;

    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
    VALUES (gen_random_uuid(),'Needed for predicinting product featuree engagement', financial_risk_assessment, feature_usage_metrics_daily, 'PENDING', jane_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(),
    feature_usage_metrics, john_id, product_owner_id, 'APPROVED', john_id, '2025-10-28 16:32:57.902449', john_id, '2025-10-28 16:32:57.910346', '2025-10-28 16:32:57.89898', '2025-10-28 16:32:57.908607', NULL);
    INSERT INTO public.role_assignments_dataset (id, dataset_id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES (gen_random_uuid(),
    feature_usage_metrics_daily, (SELECT data_product_id FROM public.datasets WHERE id = feature_usage_metrics_daily), john_id, dataset_owner_id, 'APPROVED', john_id, '2025-10-28 16:32:57.902449', john_id, '2025-10-28 16:32:57.910346', '2025-10-28 16:32:57.89898', '2025-10-28 16:32:57.908607', NULL);



    -- CEO question exploration
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at)
        VALUES (gen_random_uuid(), 'active', '{}', 'CEO Question exploration', 'ceo_question_exploration', 'explorations', 'To answer a question from the CEO', customer_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into ceo_question;
    INSERT INTO public.explorations (id, owner_id) VALUES (ceo_question, john_id);
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
        VALUES (gen_random_uuid(),'Needed for answering a question from the CEO', ceo_question, sales_performance_model_output_port, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
        VALUES (gen_random_uuid(),'Needed for answering a question from the CEO', ceo_question, inventory_management_output_port, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- COO question exploration
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at)
        VALUES (gen_random_uuid(), 'active', '{}', 'COO Question exploration', 'coo_question_exploration', 'explorations', 'To answer a question from the COO', customer_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into coo_question;
    INSERT INTO public.explorations (id, owner_id) VALUES (coo_question, jane_id);
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
        VALUES (gen_random_uuid(),'Needed for answering a question from the COO', coo_question, sales_performance_model_output_port, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.input_ports (id, justification, consuming_abstract_data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at)
        VALUES (gen_random_uuid(),'Needed for answering a question from the COO', coo_question, inventory_management_output_port, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);


    -- extra products

    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('a8afca59-78ce-4808-adaa-8bbab998ac6d', 'active', '{}', 'A/B Test Results', 'a_b_test_results', 'data_products', 'Stores and analyzes experiments to optimize product decisions.', product_development_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES ('a8afca59-78ce-4808-adaa-8bbab998ac6d', '<h2>A/B Test Results</h2><p></p><p>This data product centralizes A/B testing results for actionable insights.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Compare feature variations</li><li>Measure impact on user behavior</li><li>Support data-driven product decisions</li></ul>', '3c289333-2d55-4aed-8bd5-85015a1567fe', NULL, NULL);
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('16f9cdac-f0ab-45f9-84e1-fb28bf7eda2c', 'active', '{}', 'Product Performance Dashboard', 'product_performance_dashboard', 'data_products', 'Monitors KPIs like uptime, error rates, and adoption.', product_development_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES ('16f9cdac-f0ab-45f9-84e1-fb28bf7eda2c', '<h2>Product Performance Dashboard</h2><p></p><p>This data product provides a consolidated view of product performance metrics.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Track uptime and reliability</li><li>Monitor feature adoption</li><li>Support operational and strategic decisions</li></ul>', '1b4a64b3-96fb-404c-a73c-294802dc9852', NULL, NULL);
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('4bba2a03-b51c-4525-b094-1f85a3dba31b', 'active', '{}', 'Operational Risk Metrics', 'operational_risk_metrics', 'data_products', 'Evaluates risks in business processes to prevent disruptions.', risk_and_compliance_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES ('4bba2a03-b51c-4525-b094-1f85a3dba31b', '<h2>Operational Risk Metrics</h2><p></p><p>This data product provides centralized operational risk insights for mitigation.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Monitor business process risks</li><li>Identify vulnerabilities</li><li>Support operational continuity</li></ul>', '3c289333-2d55-4aed-8bd5-85015a1567fe', NULL, NULL);
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('92eb574f-10ec-42dc-af72-05aa06cc8ade', 'active', '{}', 'Security Incident Reporting', 'security_incident_reporting', 'data_products', 'Tracks and analyzes security breaches and attempted attacks.', risk_and_compliance_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES ('92eb574f-10ec-42dc-af72-05aa06cc8ade', '<h2>Security Incident Reporting</h2><p></p><p>This data product centralizes reporting of security incidents for response.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Track security events</li><li>Analyze incident patterns</li><li>Support rapid mitigation actions</li></ul>', '1b4a64b3-96fb-404c-a73c-294802dc9852', NULL, NULL);
    INSERT INTO public.abstract_data_products (id, status, finalizers, "name", namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('3a3dc97d-2278-42e8-8e72-dd923192a4df', 'active', '{}', 'Regulatory Audit Tracker', 'regulatory_audit_tracker', 'data_products', 'Monitors audit readiness and compliance with industry standards.', risk_and_compliance_domain_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES ('3a3dc97d-2278-42e8-8e72-dd923192a4df', '<h2>Regulatory Audit Tracker</h2><p></p><p>This data product provides a platform for tracking regulatory audit compliance.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Monitor audit readiness</li><li>Ensure regulatory adherence</li><li>Support compliance reporting</li></ul>', '1b4a64b3-96fb-404c-a73c-294802dc9852', NULL, NULL);
    INSERT INTO public.abstract_data_products (id, status, finalizers, name, namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('81815c4c-f323-4cf1-b25b-f43f231f510f', 'active', '{}', 'Biomarker discovery', 'biomarker-discovery', 'data_products', 'Helps researchers identify molecular signatures linked to disease progression or drug response.
    It accelerates translational research by combining omics data with clinical outcomes for biomarker validation.', financial_domain_id, '2025-10-28 16:32:57.885052', NULL, NULL);
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES ('81815c4c-f323-4cf1-b25b-f43f231f510f', NULL, '74b13338-aa85-4552-8ccb-7d51550c67de', data_product_lifecycle_id, NULL);
    INSERT INTO public.abstract_data_products (id, status, finalizers, name, namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('6e580d91-14ea-495e-a6d7-5db236a5c1d5', 'active', '{}', 'Clinical trial performance', 'clinical-trial-performance', 'data_products', 'Monitors progress, enrollment, and site efficiency for ongoing studies.
    It provides near–real-time visibility for clinical operations teams.', operations_and_logistics_domain_id, '2025-10-28 16:37:39.892932', NULL, NULL);
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES ('6e580d91-14ea-495e-a6d7-5db236a5c1d5', NULL, '1b4a64b3-96fb-404c-a73c-294802dc9852', data_product_lifecycle_id, NULL);
    INSERT INTO public.abstract_data_products (id, status, finalizers, name, namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('9fa5e299-fcc4-45e0-b48d-cc3deb68eefe', 'active', '{}', 'Clinical data quality monitor', 'clinical-data-quality-monitor', 'data_products', 'Automates validation and consistency checks for clinical data.
    It ensures data integrity for regulatory submissions.', operations_and_logistics_domain_id, '2025-10-28 17:56:19.863257', NULL, NULL);
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES ('9fa5e299-fcc4-45e0-b48d-cc3deb68eefe', NULL, '3c289333-2d55-4aed-8bd5-85015a1567fe', data_product_lifecycle_id, NULL);
    INSERT INTO public.abstract_data_products (id, status, finalizers, name, namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('fbcd7899-2763-4659-bd28-2a278910ef85', 'active', '{}', 'Regulatory submission tracker', 'regulatory-submission-tracker', 'data_products', 'Centralizes documentation and timelines for regulatory filings.
    It helps teams maintain compliance and track submission readiness.', operations_and_logistics_domain_id, '2025-10-28 17:59:19.849564', NULL, NULL);
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES ('fbcd7899-2763-4659-bd28-2a278910ef85', NULL, '1b4a64b3-96fb-404c-a73c-294802dc9852', data_product_lifecycle_id, NULL);
    INSERT INTO public.abstract_data_products (id, status, finalizers, name, namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('08039e5d-50a7-447a-b691-f5dc6b420dea', 'active', '{}', 'Safety Signal Detection System', 'safety-signal-detection-system', 'data_products', 'Detects early signs of drug-related adverse effects from trial and post-market data.
    It supports pharmacovigilance and regulatory risk management.', risk_and_compliance_domain_id, '2025-10-28 18:01:54.329016', NULL, NULL);
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES ('08039e5d-50a7-447a-b691-f5dc6b420dea', NULL, '90ab1128-329f-47dd-9420-c9681bfc68c4', data_product_lifecycle_id, NULL);
    INSERT INTO public.abstract_data_products (id, status, finalizers, name, namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('625b65b6-13d9-4c8c-a669-865e36fc3dfc', 'active', '{}', 'Drug Supply Chain Optimization', 'drug-supply-chain-optimization', 'data_products', 'Forecasts and manages inventory to avoid clinical supply shortages.
    It balances manufacturing throughput with site-level demand.', product_development_domain_id, '2025-10-28 18:05:44.182871', NULL, NULL);
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES ('625b65b6-13d9-4c8c-a669-865e36fc3dfc', NULL, 'f1672c38-ad1a-401a-8dd3-e0b026ab1416', data_product_lifecycle_id, NULL);
    INSERT INTO public.abstract_data_products (id, status, finalizers, name, namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('22488fe0-c30a-4447-972e-3eb22a1bd266', 'active', '{}', 'Customer intelligence platform', 'customer-intelligence-platform', 'data_products', 'Unifies healthcare professional and institutional engagement data.
    It supports more targeted and compliant outreach strategies.', commercial_and_customer_relationship_mgt_domain_id, '2025-10-28 18:09:11.673609', NULL, NULL);
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES ('22488fe0-c30a-4447-972e-3eb22a1bd266', NULL, '1b4a64b3-96fb-404c-a73c-294802dc9852', data_product_lifecycle_id, NULL);
    INSERT INTO public.abstract_data_products (id, status, finalizers, name, namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('90e65438-a942-43e0-a4a9-ee406b92df65', 'active', '{}', 'Enterprise knowledge graph', 'enterprise-knowledge-graph', 'data_products', 'Connects data entities (people, trials, compounds, documents) across all domains.
    It enables semantic search and contextual discovery within the organization.', operations_and_logistics_domain_id, '2025-10-28 18:11:47.494295', NULL, NULL);
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES ('90e65438-a942-43e0-a4a9-ee406b92df65', NULL, 'f1672c38-ad1a-401a-8dd3-e0b026ab1416', data_product_lifecycle_id, NULL);
    INSERT INTO public.abstract_data_products (id, status, finalizers, name, namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('68b28e38-3faa-45ca-9d00-3830d0a7b108', 'active', '{}', 'Employee productivity', 'employee-productivity', 'data_products', 'Measures how teams collaborate and deliver projects.
    It identifies factors influencing productivity and engagement.', customer_domain_id, '2025-10-28 18:14:07.371512', NULL, NULL);
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES ('68b28e38-3faa-45ca-9d00-3830d0a7b108', NULL, '1b4a64b3-96fb-404c-a73c-294802dc9852', data_product_lifecycle_id, NULL);
    INSERT INTO public.abstract_data_products (id, status, finalizers, name, namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('97af957a-70c4-465d-95f2-f70c11af8da0', 'active', '{}', 'DEI Insights Dashboard', 'dei-insights-dashboard', 'data_products', 'Monitors diversity, equity, and inclusion metrics across the organization.
    It ensures transparency and compliance with internal and external reporting standards.', customer_domain_id, '2025-10-28 18:16:50.70893', NULL, NULL);
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES ('97af957a-70c4-465d-95f2-f70c11af8da0', NULL, '1b4a64b3-96fb-404c-a73c-294802dc9852', data_product_lifecycle_id, NULL);
    INSERT INTO public.abstract_data_products (id, status, finalizers, name, namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('58b837a5-33d0-41cf-bf95-eb9af846f4d0', 'active', '{}', 'Patient Stratification Engine', 'patient-stratification-engine', 'data_products', 'Identifies patient subgroups most likely to respond to therapies.
    It improves trial design and treatment personalization.', operations_and_logistics_domain_id, '2025-10-28 18:29:24.833167', NULL, NULL);
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES ('58b837a5-33d0-41cf-bf95-eb9af846f4d0', NULL, '90ab1128-329f-47dd-9420-c9681bfc68c4', data_product_lifecycle_id, NULL);
    INSERT INTO public.abstract_data_products (id, status, finalizers, name, namespace, abstract_data_product_type, description, domain_id, created_on, updated_on, deleted_at) VALUES ('ccdc13fa-4a1a-4dde-ad1c-efa0d58eafb7', 'active', '{}', 'R&D Portfolio Prioritization Model', 'rd-portfolio-prioritization-model', 'data_products', 'Ranks R&D projects based on scientific potential, ROI, and strategic fit.
    It provides leadership with an objective decision framework for resource allocation.', operations_and_logistics_domain_id, '2025-10-28 18:34:32.308251', NULL, NULL);
    INSERT INTO public.data_products (id, about, type_id, lifecycle_id, usage) VALUES ('ccdc13fa-4a1a-4dde-ad1c-efa0d58eafb7', NULL, 'f1672c38-ad1a-401a-8dd3-e0b026ab1416', data_product_lifecycle_id, NULL);

    -- DATASETS
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('bab58ea1-0ccd-44f1-8d75-634822b6b95b', 'ab_test_outcomes', 'a8afca59-78ce-4808-adaa-8bbab998ac6d', 'Ab Test Outcomes', 'Results of A/B experiments per cohort', 'Provides experiment insights to inform product decisions. Key objectives: - Measure feature impact - Optimize UX - Support iteration', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('910a6eb4-fc3e-413b-bafa-b6b2666ca6e3', 'experiment_variants_comparison', 'a8afca59-78ce-4808-adaa-8bbab998ac6d', 'Experiment Variants Comparison', 'Comparison of different experiment variants', 'Enables detailed analysis of experimental results. Key objectives: - Identify best-performing variant - Support hypothesis validation - Guide feature rollout', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('03ff0760-1bed-4805-ad77-644d281f1f22', 'product_kpi_dashboard', '16f9cdac-f0ab-45f9-84e1-fb28bf7eda2c', 'Product KPI Dashboard', 'Uptime, error rates, adoption metrics', 'Provides high-level performance metrics for products. Key objectives: - Track health and reliability - Support operations - Enable strategic decisions', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('fcd61536-b8db-4f83-bd62-ee8ed7c3031a', 'operational_risk_report', '4bba2a03-b51c-4525-b094-1f85a3dba31b', 'Operational Risk Report', 'KPIs for process and operational risks', 'Provides insight into operational vulnerabilities. Key objectives: - Monitor risks - Mitigate disruptions - Support continuity planning', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('8a4f5df8-4b5c-4290-a8e2-c8ec42713b7c', 'security_incident_summary', '92eb574f-10ec-42dc-af72-05aa06cc8ade', 'Security Incident Summary', 'Report on security events and breaches', 'Provides consolidated view of security incidents. Key objectives: - Track threats - Analyze patterns - Support mitigation', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, created_on, updated_on, deleted_at) VALUES ('f1659a4f-95d5-40bb-a7b5-121cf7e74ea8', 'regulatory_audit_report', '3a3dc97d-2278-42e8-8e72-dd923192a4df', 'Regulatory Audit Report', 'Audit compliance metrics and findings', 'Provides regulatory audit insights. Key objectives: - Monitor compliance - Prepare for audits - Support executive reporting', 'ACTIVE', 'RESTRICTED', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);



    -- Data output configurations
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('b6bc5710-8706-45fb-bf85-6ed90d8a7428', 'GlueTechnicalAssetConfiguration') ;
    INSERT INTO public.glue_technical_asset_configurations(id, bucket_identifier, "database", database_suffix, "table", table_path, access_granularity, database_path, created_on, updated_on, deleted_at) VALUES ('b6bc5710-8706-45fb-bf85-6ed90d8a7428', 'datalake', 'pharma_research', 'glue_output', '*', '*', 'schema', 'pharma_research', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into glue_configuration_id;
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('cdd627e5-08b2-4dc8-add6-32ff569f543b', 'DatabricksTechnicalAssetConfiguration');
    INSERT INTO public.databricks_technical_asset_configurations (id, bucket_identifier, "catalog", schema, catalog_path, table_path, "table", access_granularity, created_on, updated_on, deleted_at) VALUES ('cdd627e5-08b2-4dc8-add6-32ff569f543b', 'datalake', 'pharma_research', 'databricks_output', '', '', 'pharma_research', 'table', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into databricks_configuration_id;


    -- Data product settings
    INSERT INTO public.data_product_settings (id, namespace, name, "default", "order", type, tooltip, category, scope) VALUES ('e12ec335-d7a4-4e27-8225-b66da70f3158', 'iam_role', 'IAM service accounts', 'false', '100', 'CHECKBOX', 'Generate IAM access credentials for this data product', 'AWS', 'DATAPRODUCT');

      -- DATA OUTPUTS
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('b4caa471-99a2-40e3-9d43-67b85e466c5b', 'omics-data', 'Omics data', 'Captures genomic, proteomic, and transcriptomic measurements from lab experiments to provide a unified dataset for biomarker exploration.', 'ACTIVE', returned_platform_id, glue_service_id, '81815c4c-f323-4cf1-b25b-f43f231f510f', NULL, '12346cc6-f58d-4217-88d3-6443b01d5d0f', '2025-10-28 16:34:02.355842', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('86d75ebd-8c3a-4c71-b5a5-33146b28b410', 'clinical-outcome-correlation', 'Clinical outcome correlation', 'Links omics samples to anonymized patient outcomes, enabling downstream hypothesis testing.', 'ACTIVE', 'baa5c47b-805a-4cbb-ad8b-038c66e81b7e', 'ce208413-b629-44d2-9f98-e5b47a315a56', '81815c4c-f323-4cf1-b25b-f43f231f510f', NULL, 'db8e84e9-e942-4ebb-ac78-ee0fa600db5d', '2025-10-28 16:34:31.5612', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('904ccfd4-c5e5-4a0d-af0b-3a3c38b34696', 'trial-master-summary', 'Trial master summary', 'Central repository for study metadata and milestones.', 'ACTIVE', returned_platform_id, glue_service_id, '6e580d91-14ea-495e-a6d7-5db236a5c1d5', NULL, '17798a65-12e2-4a5e-84c0-9948041849e0', '2025-10-28 16:38:29.452913', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('77951289-2f2c-46f3-a3e4-b4ba17fab169', 'enrollment-and-retention-metrics', 'Enrollment and retention metrics', 'Tracks patient recruitment and retention trends per site.', 'ACTIVE', returned_platform_id, glue_service_id, '6e580d91-14ea-495e-a6d7-5db236a5c1d5', NULL, '08877d52-a5c1-4fd4-8e8d-ca3c108f2363', '2025-10-28 16:39:02.184116', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('c006b4a3-6840-4aa9-966d-21acc8d18366', 'ecrf-data-logs', 'ECRF data logs', 'Capture all clinical entries and edits in electronic forms.', 'ACTIVE', returned_platform_id, glue_service_id, '9fa5e299-fcc4-45e0-b48d-cc3deb68eefe', NULL, '43a09ac9-9576-4436-94f7-79339510c887', '2025-10-28 17:56:57.829806', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('fbd3dbdf-76f1-4c0a-b732-66f1be456860', 'data-validation-results', 'Data validation results', 'Stores outcomes of automated QC rules and anomalies.', 'ACTIVE', returned_platform_id, glue_service_id, '9fa5e299-fcc4-45e0-b48d-cc3deb68eefe', NULL, '3871765b-881b-4654-a0ec-7e1db6a2de2f', '2025-10-28 17:57:32.996449', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('d3f02123-b777-40b9-8c52-0ec66be68241', 'submission-package-metadata', 'Submission Package Metadata', 'Contains submission components and status per agency.', 'ACTIVE', returned_platform_id, glue_service_id, 'fbcd7899-2763-4659-bd28-2a278910ef85', NULL, '3f9ba1f0-84fb-4a5c-858d-11b1bca33b6b', '2025-10-28 17:59:45.865277', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('361d6347-afd8-4927-af8b-ce5dc54cca96', 'compliance-audit-trail', 'Compliance Audit Trail', 'Logs document revisions and quality issues.', 'ACTIVE', returned_platform_id, s3_service_id, 'fbcd7899-2763-4659-bd28-2a278910ef85', NULL, 'b1a77a22-5dac-4631-9e22-b6129c67d037', '2025-10-28 18:00:21.273949', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('561d2ab6-b9dc-405a-9190-8f2d3d443b28', 'adverse-event-database', 'Adverse event database', 'Collects standardized AE reports from multiple data sources.
    Output: Consolidated case-level dataset for signal analysis.', 'ACTIVE', returned_platform_id, s3_service_id, '08039e5d-50a7-447a-b691-f5dc6b420dea', NULL, '10889f18-7156-4617-84f7-89aac3370027', '2025-10-28 18:02:28.302038', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('9db5db83-a92b-4111-a0b6-dfe43fdc9454', 'signal-analytics-output', 'Signal analytics output', 'Aggregates statistical disproportionality metrics for safety signals.', 'ACTIVE', returned_platform_id, s3_service_id, '08039e5d-50a7-447a-b691-f5dc6b420dea', NULL, '2cd814a6-20fe-430e-ba62-ace42b10897e', '2025-10-28 18:03:02.685892', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('fcbc3477-62cd-43ff-843f-bb18e24d31be', 'manufacturing-batch-data', 'Manufacturing Batch Data', 'Tracks production and quality of drug lots', 'ACTIVE', returned_platform_id, s3_service_id, '625b65b6-13d9-4c8c-a669-865e36fc3dfc', NULL, '83e1a9e2-19ec-4b31-aeb5-40ac81e3e27c', '2025-10-28 18:06:26.226197', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('2aa6122b-833f-4386-894d-4a5af3af10c4', 'shipment-logs', 'Shipment logs', 'Records product shipments', 'ACTIVE', returned_platform_id, s3_service_id, '625b65b6-13d9-4c8c-a669-865e36fc3dfc', NULL, 'f8df446d-0211-4ee8-81e1-5410b6419e6e', '2025-10-28 18:07:05.924953', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('c15caa28-c063-4e41-8dd3-c5cccccfa88c', 'site-inventory', 'Site inventory', 'Shows the stock levels at trial sites.', 'ACTIVE', returned_platform_id, s3_service_id, '625b65b6-13d9-4c8c-a669-865e36fc3dfc', NULL, '7bb075e0-70c3-44c2-811e-cd7bba757927', '2025-10-28 18:07:33.673309', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('d1092134-aac6-4501-88ba-464a9f0cedc8', 'customer-master-data', 'Customer master data', 'Maintains a golden record of HCPs and organizations.', 'ACTIVE', 'baa5c47b-805a-4cbb-ad8b-038c66e81b7e', 'ce208413-b629-44d2-9f98-e5b47a315a56', '22488fe0-c30a-4447-972e-3eb22a1bd266', NULL, 'dc1cc43b-698e-424c-af5b-27f68f0c0781', '2025-10-28 18:09:39.615998', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('1e9030f0-6e6e-485e-8bd9-0ff76bfc371f', 'engagement-activity-log', 'Engagement Activity Log', 'Tracks calls, emails, and events with customers.', 'ACTIVE', 'baa5c47b-805a-4cbb-ad8b-038c66e81b7e', 'ce208413-b629-44d2-9f98-e5b47a315a56', '22488fe0-c30a-4447-972e-3eb22a1bd266', NULL, '8d18f556-ccd2-425e-8e48-f24c185a053e', '2025-10-28 18:10:04.633488', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('07fe77b2-f06f-4692-a76b-acdd2c412db3', 'entity-registry', 'Entity Registry', 'Stores canonical identifiers and metadata for all business entities.', 'ACTIVE', 'baa5c47b-805a-4cbb-ad8b-038c66e81b7e', 'ce208413-b629-44d2-9f98-e5b47a315a56', '90e65438-a942-43e0-a4a9-ee406b92df65', NULL, 'da19237f-eaf6-4a0a-8090-a2b724189978', '2025-10-28 18:12:07.053708', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('967ca866-d868-49b8-9a31-3d2e97ed63f3', 'relationship-graph', 'Relationship Graph', 'Maps inter-entity relationships across domains.', 'ACTIVE', 'baa5c47b-805a-4cbb-ad8b-038c66e81b7e', 'ce208413-b629-44d2-9f98-e5b47a315a56', '90e65438-a942-43e0-a4a9-ee406b92df65', NULL, '502d4484-e332-4854-a2d8-7c387906f459', '2025-10-28 18:12:22.129267', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('e1024306-a524-4142-8673-b0219dfad76b', 'project-delivery-metrics', 'Project Delivery Metrics', 'Tracks timelines, milestones, and outcomes of internal projects.', 'ACTIVE', returned_platform_id, glue_service_id, '68b28e38-3faa-45ca-9d00-3830d0a7b108', NULL, 'af1e8de6-3dc8-43e5-9c74-597c5676c137', '2025-10-28 18:14:25.794897', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('dcf5270d-562b-4cd1-a0a3-c0835003698b', 'employee-kpi-log', 'Employee KPI log', 'Tracks how well each employee is performing with respect to their set KPIs', 'ACTIVE', returned_platform_id, glue_service_id, '68b28e38-3faa-45ca-9d00-3830d0a7b108', NULL, '677a9352-a968-44be-a5df-6e5e4094ebe7', '2025-10-28 18:15:10.920954', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('cce652d7-b6a6-4000-a248-4cc9d9066fab', 'workforce-demographics', 'Workforce Demographics', 'Records representation by gender, age, and level.', 'ACTIVE', 'baa5c47b-805a-4cbb-ad8b-038c66e81b7e', 'ce208413-b629-44d2-9f98-e5b47a315a56', '97af957a-70c4-465d-95f2-f70c11af8da0', NULL, '44daa0b4-a027-4e5b-b233-b8342da71c38', '2025-10-28 18:17:04.80167', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('a686ff78-3039-4006-9dd1-e8d5cf293ec7', 'compensation-equity-data', 'Compensation Equity Data', 'Captures pay and benefits information across roles.', 'ACTIVE', 'baa5c47b-805a-4cbb-ad8b-038c66e81b7e', 'ce208413-b629-44d2-9f98-e5b47a315a56', '97af957a-70c4-465d-95f2-f70c11af8da0', NULL, 'e0875fbb-f2ff-4804-a9ba-c9c3b006fca3', '2025-10-28 18:17:20.241114', NULL, NULL, 'default');

    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('0473d934-3993-45d5-9d25-151162f673da', 'patient-demographic', 'Patient demographic', 'Stores baseline info about trial participants', 'ACTIVE', returned_platform_id, glue_service_id, '58b837a5-33d0-41cf-bf95-eb9af846f4d0', NULL, '74db2ed9-b28a-4875-8eb5-17b9fe445c8d', '2025-10-28 18:30:00.415068', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('975b129b-d9c4-4a8a-8430-9be3be621c37', 'patient-clinical-profile', 'Patient clinical profile', 'Stores basic clinical information about the patients', 'ACTIVE', returned_platform_id, glue_service_id, '58b837a5-33d0-41cf-bf95-eb9af846f4d0', NULL, '22e9a60d-e8f8-4bf5-9efd-500f407dbb47', '2025-10-28 18:30:28.256785', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('b4b4ba5e-1c1a-42f8-9017-25fed591f30b', 'response-to-treatment', 'Response to treatment', 'Records treatment outcomes and biomarkers linked to each patient.', 'ACTIVE', returned_platform_id, glue_service_id, '58b837a5-33d0-41cf-bf95-eb9af846f4d0', NULL, '2ea14ab5-a45b-4799-86fc-d6285377a4d6', '2025-10-28 18:30:57.415321', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('2458ead6-6361-4542-a5aa-5ce45cba4aa3', 'competitive-intelligence', 'Competitive Intelligence ', 'Aggregates competitor activity, publications, and pipeline updates.', 'ACTIVE', returned_platform_id, glue_service_id, 'ccdc13fa-4a1a-4dde-ad1c-efa0d58eafb7', NULL, 'bbed68d4-8bda-420a-a6cf-37cb32ba9d45', '2025-10-28 18:35:42.552188', NULL, NULL, 'default');
    INSERT INTO public.data_outputs (id, namespace, name, description, status, platform_id, service_id, owner_id, configuration, configuration_id, created_on, updated_on, deleted_at, "technical_mapping") VALUES ('eb93308b-a5bb-4f19-90e3-cf56b0855a07', 'rd-program-ranking', 'R&D program ranking', 'Ranking of the different R&D programs within our organisation', 'ACTIVE', returned_platform_id, glue_service_id, 'ccdc13fa-4a1a-4dde-ad1c-efa0d58eafb7', NULL, '8b6b6b35-c155-4f13-a847-c7598b08cea9', '2025-10-28 18:36:26.66997', NULL, NULL, 'default');

    -- extra data output configurations
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('12346cc6-f58d-4217-88d3-6443b01d5d0f', 'GlueTechnicalAssetConfiguration');
    INSERT INTO public.glue_technical_asset_configurations (id, bucket_identifier, "database", database_suffix, "table", database_path, table_path, access_granularity, created_on, updated_on, deleted_at) VALUES ('12346cc6-f58d-4217-88d3-6443b01d5d0f', '', 'biomarker-discovery', '', 'omics_prod', 'biomarker-discovery', 'omics_prod', 'table', '2025-10-28 16:34:02.355842', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('db8e84e9-e942-4ebb-ac78-ee0fa600db5d', 'DatabricksTechnicalAssetConfiguration');
    INSERT INTO public.databricks_technical_asset_configurations (id, bucket_identifier, "catalog", schema, catalog_path, table_path, "table", access_granularity, created_on, updated_on, deleted_at) VALUES ('db8e84e9-e942-4ebb-ac78-ee0fa600db5d', '', 'biomarker-discovery', '', 'biomarker-discovery', 'clinical_correlation', 'clinical_correlation', 'table', '2025-10-28 16:34:31.5612', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('17798a65-12e2-4a5e-84c0-9948041849e0', 'GlueTechnicalAssetConfiguration');
    INSERT INTO public.glue_technical_asset_configurations (id, bucket_identifier, "database", database_suffix, "table", database_path, table_path, access_granularity, created_on, updated_on, deleted_at) VALUES ('17798a65-12e2-4a5e-84c0-9948041849e0', '', 'clinical-trial-performance', '', 'trial_master', 'clinical-trial-performance', 'trial_master', 'table', '2025-10-28 16:38:29.452913', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('08877d52-a5c1-4fd4-8e8d-ca3c108f2363', 'GlueTechnicalAssetConfiguration');
    INSERT INTO public.glue_technical_asset_configurations (id, bucket_identifier, "database", database_suffix, "table", database_path, table_path, access_granularity, created_on, updated_on, deleted_at) VALUES ('08877d52-a5c1-4fd4-8e8d-ca3c108f2363', '', 'clinical-trial-performance', '', 'retention_metrics', 'clinical-trial-performance', 'retention_metrics', 'table', '2025-10-28 16:39:02.184116', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('43a09ac9-9576-4436-94f7-79339510c887', 'GlueTechnicalAssetConfiguration');
    INSERT INTO public.glue_technical_asset_configurations (id, bucket_identifier, "database", database_suffix, "table", database_path, table_path, access_granularity, created_on, updated_on, deleted_at) VALUES ('43a09ac9-9576-4436-94f7-79339510c887', '', 'clinical-data-quality-monitor', '', '*', 'clinical-data-quality-monitor', '*', 'table', '2025-10-28 17:56:57.829806', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('3871765b-881b-4654-a0ec-7e1db6a2de2f', 'GlueTechnicalAssetConfiguration');
    INSERT INTO public.glue_technical_asset_configurations (id, bucket_identifier, "database", database_suffix, "table", database_path, table_path, access_granularity, created_on, updated_on, deleted_at) VALUES ('3871765b-881b-4654-a0ec-7e1db6a2de2f', '', 'clinical-data-quality-monitor', '', 'clinical_data_quality', 'clinical-data-quality-monitor', 'clinical_data_quality', 'table', '2025-10-28 17:57:32.996449', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('3f9ba1f0-84fb-4a5c-858d-11b1bca33b6b', 'GlueTechnicalAssetConfiguration');
    INSERT INTO public.glue_technical_asset_configurations (id, bucket_identifier, "database", database_suffix, "table", database_path, table_path, access_granularity, created_on, updated_on, deleted_at) VALUES ('3f9ba1f0-84fb-4a5c-858d-11b1bca33b6b', '', 'regulatory-submission-tracker', '', '*', 'regulatory-submission-tracker', '*', 'table', '2025-10-28 17:59:45.865277', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('b1a77a22-5dac-4631-9e22-b6129c67d037', 'S3TechnicalAssetConfiguration');
    INSERT INTO public.s3_technical_asset_configurations (id, bucket, suffix, path, created_on, updated_on, deleted_at) VALUES ('b1a77a22-5dac-4631-9e22-b6129c67d037', 'datalake', 'regulatory-submission-tracker', 'compliance-audit-trail', '2025-10-28 18:00:21.273949', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('10889f18-7156-4617-84f7-89aac3370027', 'S3TechnicalAssetConfiguration');
    INSERT INTO public.s3_technical_asset_configurations (id, bucket, suffix, path, created_on, updated_on, deleted_at) VALUES ('10889f18-7156-4617-84f7-89aac3370027', 'datalake', 'safety-signal-detection-system', 'adverse-event-db', '2025-10-28 18:02:28.302038', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('2cd814a6-20fe-430e-ba62-ace42b10897e', 'S3TechnicalAssetConfiguration');
    INSERT INTO public.s3_technical_asset_configurations (id, bucket, suffix, path, created_on, updated_on, deleted_at) VALUES ('2cd814a6-20fe-430e-ba62-ace42b10897e', 'datalake', 'safety-signal-detection-system', 'signal-analytics', '2025-10-28 18:03:02.685892', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('83e1a9e2-19ec-4b31-aeb5-40ac81e3e27c', 'S3TechnicalAssetConfiguration');
    INSERT INTO public.s3_technical_asset_configurations (id, bucket, suffix, path, created_on, updated_on, deleted_at) VALUES ('83e1a9e2-19ec-4b31-aeb5-40ac81e3e27c', 'datalake', 'drug-supply-chain-optimization', 'manufactoring', '2025-10-28 18:06:26.226197', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('f8df446d-0211-4ee8-81e1-5410b6419e6e', 'S3TechnicalAssetConfiguration');
    INSERT INTO public.s3_technical_asset_configurations (id, bucket, suffix, path, created_on, updated_on, deleted_at) VALUES ('f8df446d-0211-4ee8-81e1-5410b6419e6e', 'datalake', 'drug-supply-chain-optimization', 'shipment-logs', '2025-10-28 18:07:05.924953', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('7bb075e0-70c3-44c2-811e-cd7bba757927', 'S3TechnicalAssetConfiguration');
    INSERT INTO public.s3_technical_asset_configurations (id, bucket, suffix, path, created_on, updated_on, deleted_at) VALUES ('7bb075e0-70c3-44c2-811e-cd7bba757927', 'datalake', 'drug-supply-chain-optimization', 'site-inventory', '2025-10-28 18:07:33.673309', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('dc1cc43b-698e-424c-af5b-27f68f0c0781', 'DatabricksTechnicalAssetConfiguration');
    INSERT INTO public.databricks_technical_asset_configurations (id, bucket_identifier, "catalog", schema, catalog_path, table_path, "table", access_granularity, created_on, updated_on, deleted_at) VALUES ('dc1cc43b-698e-424c-af5b-27f68f0c0781', '', 'customer-intelligence-platform', '', 'customer-intelligence-platform', 'custmer-master-data', 'custmer-master-data', 'table', '2025-10-28 18:09:39.615998', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('8d18f556-ccd2-425e-8e48-f24c185a053e', 'DatabricksTechnicalAssetConfiguration');
    INSERT INTO public.databricks_technical_asset_configurations (id, bucket_identifier, "catalog", schema, catalog_path, table_path, "table", access_granularity, created_on, updated_on, deleted_at) VALUES ('8d18f556-ccd2-425e-8e48-f24c185a053e', '', 'customer-intelligence-platform', '', 'customer-intelligence-platform', 'engagement-activity', 'engagement-activity', 'table', '2025-10-28 18:10:04.633488', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('da19237f-eaf6-4a0a-8090-a2b724189978', 'DatabricksTechnicalAssetConfiguration');
    INSERT INTO public.databricks_technical_asset_configurations (id, bucket_identifier, "catalog", schema, catalog_path, table_path, "table", access_granularity, created_on, updated_on, deleted_at) VALUES ('da19237f-eaf6-4a0a-8090-a2b724189978', '', 'enterprise-knowledge-graph', '', 'enterprise-knowledge-graph', '*', '*', 'table', '2025-10-28 18:12:07.053708', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('502d4484-e332-4854-a2d8-7c387906f459', 'DatabricksTechnicalAssetConfiguration');
    INSERT INTO public.databricks_technical_asset_configurations (id, bucket_identifier, "catalog", schema, catalog_path, table_path, "table", access_granularity, created_on, updated_on, deleted_at) VALUES ('502d4484-e332-4854-a2d8-7c387906f459', '', 'enterprise-knowledge-graph', '', 'enterprise-knowledge-graph', '*', '*', 'table', '2025-10-28 18:12:22.129267', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('af1e8de6-3dc8-43e5-9c74-597c5676c137', 'GlueTechnicalAssetConfiguration');
    INSERT INTO public.glue_technical_asset_configurations (id, bucket_identifier, "database", database_suffix, "table", database_path, table_path, access_granularity, created_on, updated_on, deleted_at) VALUES ('af1e8de6-3dc8-43e5-9c74-597c5676c137', '', 'employee-productivity', '', '*', 'employee-productivity', '*', 'table', '2025-10-28 18:14:25.794897', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('677a9352-a968-44be-a5df-6e5e4094ebe7', 'GlueTechnicalAssetConfiguration');
    INSERT INTO public.glue_technical_asset_configurations (id, bucket_identifier, "database", database_suffix, "table", database_path, table_path, access_granularity, created_on, updated_on, deleted_at) VALUES ('677a9352-a968-44be-a5df-6e5e4094ebe7', '', 'employee-productivity', '', '*', 'employee-productivity', '*', 'table', '2025-10-28 18:15:10.920954', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('44daa0b4-a027-4e5b-b233-b8342da71c38', 'DatabricksTechnicalAssetConfiguration');
    INSERT INTO public.databricks_technical_asset_configurations (id, bucket_identifier, "catalog", schema, catalog_path, table_path, "table", access_granularity, created_on, updated_on, deleted_at) VALUES ('44daa0b4-a027-4e5b-b233-b8342da71c38', '', 'dei-insights-dashboard', '', 'dei-insights-dashboard', '*', '*', 'table', '2025-10-28 18:17:04.80167', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('e0875fbb-f2ff-4804-a9ba-c9c3b006fca3', 'DatabricksTechnicalAssetConfiguration');
    INSERT INTO public.databricks_technical_asset_configurations (id, bucket_identifier, "catalog", schema, catalog_path, table_path, "table", access_granularity, created_on, updated_on, deleted_at) VALUES ('e0875fbb-f2ff-4804-a9ba-c9c3b006fca3', '', 'dei-insights-dashboard', '', 'dei-insights-dashboard', '*', '*', 'table', '2025-10-28 18:17:20.241114', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('ff632a7d-4ddd-4fd1-800a-ba8098c26c18', 'GlueTechnicalAssetConfiguration');
    INSERT INTO public.glue_technical_asset_configurations (id, bucket_identifier, "database", database_suffix, "table", database_path, table_path, access_granularity, created_on, updated_on, deleted_at) VALUES ('ff632a7d-4ddd-4fd1-800a-ba8098c26c18', '', 'sales-performance-model', '', '*', 'sales-performance-model', '*', 'table', '2025-10-28 18:19:44.674412', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('e8129149-bdb5-4c15-8211-4b6b83fcb64a', 'GlueTechnicalAssetConfiguration');
    INSERT INTO public.glue_technical_asset_configurations (id, bucket_identifier, "database", database_suffix, "table", database_path, table_path, access_granularity, created_on, updated_on, deleted_at) VALUES ('e8129149-bdb5-4c15-8211-4b6b83fcb64a', '', 'sales-performance-model', '', '*', 'sales-performance-model', '*', 'table', '2025-10-28 18:20:01.401722', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('74db2ed9-b28a-4875-8eb5-17b9fe445c8d', 'GlueTechnicalAssetConfiguration');
    INSERT INTO public.glue_technical_asset_configurations (id, bucket_identifier, "database", database_suffix, "table", database_path, table_path, access_granularity, created_on, updated_on, deleted_at) VALUES ('74db2ed9-b28a-4875-8eb5-17b9fe445c8d', '', 'patient-stratification-engine', '', '*', 'patient-stratification-engine', '*', 'table', '2025-10-28 18:30:00.415068', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('22e9a60d-e8f8-4bf5-9efd-500f407dbb47', 'GlueTechnicalAssetConfiguration');
    INSERT INTO public.glue_technical_asset_configurations (id, bucket_identifier, "database", database_suffix, "table", database_path, table_path, access_granularity, created_on, updated_on, deleted_at) VALUES ('22e9a60d-e8f8-4bf5-9efd-500f407dbb47', '', 'patient-stratification-engine', '', '*', 'patient-stratification-engine', '*', 'table', '2025-10-28 18:30:28.256785', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('2ea14ab5-a45b-4799-86fc-d6285377a4d6', 'GlueTechnicalAssetConfiguration');
    INSERT INTO public.glue_technical_asset_configurations (id, bucket_identifier, "database", database_suffix, "table", database_path, table_path, access_granularity, created_on, updated_on, deleted_at) VALUES ('2ea14ab5-a45b-4799-86fc-d6285377a4d6', '', 'patient-stratification-engine', '', '*', 'patient-stratification-engine', '*', 'table', '2025-10-28 18:30:57.415321', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('bbed68d4-8bda-420a-a6cf-37cb32ba9d45', 'GlueTechnicalAssetConfiguration');
    INSERT INTO public.glue_technical_asset_configurations (id, bucket_identifier, "database", database_suffix, "table", database_path, table_path, access_granularity, created_on, updated_on, deleted_at) VALUES ('bbed68d4-8bda-420a-a6cf-37cb32ba9d45', '', 'rd-portfolio-prioritization-model', '', '*', 'rd-portfolio-prioritization-model', '*', 'table', '2025-10-28 18:35:42.552188', NULL, NULL);
    INSERT INTO public.data_output_configurations (id, configuration_type) VALUES ('8b6b6b35-c155-4f13-a847-c7598b08cea9', 'GlueTechnicalAssetConfiguration');
    INSERT INTO public.glue_technical_asset_configurations (id, bucket_identifier, "database", database_suffix, "table", database_path, table_path, access_granularity, created_on, updated_on, deleted_at) VALUES ('8b6b6b35-c155-4f13-a847-c7598b08cea9', '', 'rd-portfolio-prioritization-model', '', '*', 'rd-portfolio-prioritization-model', '*', 'table', '2025-10-28 18:36:26.66997', NULL, NULL);

-- INSERT ROLE ASSIGNMENTS FOR DATA PRODUCTS
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at)VALUES ('3502276b-b9b3-47f2-901b-3c4502fb7d1e', '81815c4c-f323-4cf1-b25b-f43f231f510f', john_id, product_owner_id, 'APPROVED', john_id, '2025-10-28 16:32:57.902449', john_id, '2025-10-28 16:32:57.910346', '2025-10-28 16:32:57.89898', '2025-10-28 16:32:57.908607', NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES ('5a1f650c-a4cf-4a59-825c-08fa699617ca', '6e580d91-14ea-495e-a6d7-5db236a5c1d5', jane_id, product_owner_id, 'APPROVED', john_id, '2025-10-28 16:37:39.90644', john_id, '2025-10-28 16:37:39.917665', '2025-10-28 16:37:39.901065', '2025-10-28 16:37:39.914117', NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES ('4c94a3f1-1fd3-44ea-aef2-c220773eb969', '6e580d91-14ea-495e-a6d7-5db236a5c1d5', john_id, product_owner_id, 'APPROVED', john_id, '2025-10-28 16:41:33.829482', john_id, '2025-10-28 16:41:33.839374', '2025-10-28 16:41:33.822617', '2025-10-28 16:41:33.836909', NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES ('da86ebb4-5e20-4be8-88ed-3d33a890c7a9', '9fa5e299-fcc4-45e0-b48d-cc3deb68eefe', john_id, product_owner_id, 'APPROVED', john_id, '2025-10-28 17:56:19.876226', john_id, '2025-10-28 17:56:19.881112', '2025-10-28 17:56:19.873821', '2025-10-28 17:56:19.880351', NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES ('d3695c76-2163-41f7-bff7-bd1dedcc8096', 'fbcd7899-2763-4659-bd28-2a278910ef85', john_id, product_owner_id, 'APPROVED', john_id, '2025-10-28 17:59:19.862559', john_id, '2025-10-28 17:59:19.8694', '2025-10-28 17:59:19.858731', '2025-10-28 17:59:19.867782', NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES ('bfac90c4-9290-472b-9123-0b2f4ae45d2e', 'fbcd7899-2763-4659-bd28-2a278910ef85', jane_id, product_owner_id, 'APPROVED', john_id, '2025-10-28 17:59:19.88175', john_id, '2025-10-28 17:59:19.887169', '2025-10-28 17:59:19.874011', '2025-10-28 17:59:19.885869', NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES ('5c6f6c98-1401-4ca1-a577-0a9e8db701a9', '08039e5d-50a7-447a-b691-f5dc6b420dea', jane_id, product_owner_id, 'APPROVED', john_id, '2025-10-28 18:01:54.338886', john_id, '2025-10-28 18:01:54.343617', '2025-10-28 18:01:54.336493', '2025-10-28 18:01:54.342708', NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES ('54b4577d-f571-4d53-99e5-e83380c47438', '08039e5d-50a7-447a-b691-f5dc6b420dea', john_id, product_owner_id, 'APPROVED', john_id, '2025-10-28 18:01:54.352817', john_id, '2025-10-28 18:01:54.356766', '2025-10-28 18:01:54.347504', '2025-10-28 18:01:54.356012', NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES ('7c5123ac-0e60-43a1-bdfd-54ff59d4164c', '625b65b6-13d9-4c8c-a669-865e36fc3dfc', john_id, product_owner_id, 'APPROVED', john_id, '2025-10-28 18:05:44.192946', john_id, '2025-10-28 18:05:44.198121', '2025-10-28 18:05:44.190775', '2025-10-28 18:05:44.197289', NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES ('44cec659-3489-447d-850f-c8ea65ec6f5a', '22488fe0-c30a-4447-972e-3eb22a1bd266', john_id, product_owner_id, 'APPROVED', john_id, '2025-10-28 18:09:11.683137', john_id, '2025-10-28 18:09:11.688498', '2025-10-28 18:09:11.679884', '2025-10-28 18:09:11.6877', NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES ('7676860f-32be-49b2-adbf-85087ce9da9d', '90e65438-a942-43e0-a4a9-ee406b92df65', john_id, product_owner_id, 'APPROVED', john_id, '2025-10-28 18:11:47.504193', john_id, '2025-10-28 18:11:47.508956', '2025-10-28 18:11:47.502037', '2025-10-28 18:11:47.508201', NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES ('8591f923-2696-4aa6-98ed-e396c7cb2ded', '68b28e38-3faa-45ca-9d00-3830d0a7b108', john_id, product_owner_id, 'APPROVED', john_id, '2025-10-28 18:14:07.388736', john_id, '2025-10-28 18:14:07.394139', '2025-10-28 18:14:07.385202', '2025-10-28 18:14:07.393015', NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES ('437b00ab-7473-4a31-b5ff-f15794d9b56e', '97af957a-70c4-465d-95f2-f70c11af8da0', john_id, product_owner_id, 'APPROVED', john_id, '2025-10-28 18:16:50.723993', john_id, '2025-10-28 18:16:50.72973', '2025-10-28 18:16:50.720213', '2025-10-28 18:16:50.728845', NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES ('9ef6eaae-f46e-440a-8cd6-88d30de94516', '86b74246-734f-4cea-a984-3dd0d27fc565', john_id, product_owner_id, 'APPROVED', john_id, '2025-10-28 18:19:20.46085', john_id, '2025-10-28 18:19:20.465528', '2025-10-28 18:19:20.458588', '2025-10-28 18:19:20.464641', NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES ('884c0d5e-e442-4bdf-8a67-c0e752e80d86', '58b837a5-33d0-41cf-bf95-eb9af846f4d0', john_id, product_owner_id, 'APPROVED', john_id, '2025-10-28 18:29:24.843296', john_id, '2025-10-28 18:29:24.848553', '2025-10-28 18:29:24.841102', '2025-10-28 18:29:24.847524', NULL);
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_by_id, requested_on, decided_by_id, decided_on, created_on, updated_on, deleted_at) VALUES ('240dbbb2-ea7f-4900-8a02-30ec084e0a5d', 'ccdc13fa-4a1a-4dde-ad1c-efa0d58eafb7', john_id, product_owner_id, 'APPROVED', john_id, '2025-10-28 18:34:32.318606', john_id, '2025-10-28 18:34:32.323823', '2025-10-28 18:34:32.316108', '2025-10-28 18:34:32.323078', NULL);

    -- ------------------------------------------------------------------------------------------------
    -- START of Insert dynamic dataset query stats
    -- ------------------------------------------------------------------------------------------------

    -- 1. Sales performance (adding 4 to test the other category aggregation)

    -- Single-query daily consumer over the last six months
    INSERT INTO public.dataset_query_stats_daily (date, dataset_id, consumer_data_product_id, query_count)
    SELECT gs::date, sales_performance_model_output_port, revenue_dashboard, 1
    FROM generate_series((CURRENT_DATE - INTERVAL '6 months')::date, CURRENT_DATE - 1, INTERVAL '1 day') AS gs;

    -- -- Ten weekday queries for the last four months
    INSERT INTO public.dataset_query_stats_daily (date, dataset_id, consumer_data_product_id, query_count)
    SELECT gs::date, sales_performance_model_output_port, cash_flow_monitoring, 10
    FROM generate_series((CURRENT_DATE - INTERVAL '4 months')::date, CURRENT_DATE - 1, INTERVAL '1 day') AS gs
    WHERE EXTRACT(ISODOW FROM gs) BETWEEN 1 AND 5;

    -- -- Weekly Monday pings (consumer #3)
    INSERT INTO public.dataset_query_stats_daily (date, dataset_id, consumer_data_product_id, query_count)
    SELECT gs::date, sales_performance_model_output_port, fraud_detection, 3
    FROM generate_series((CURRENT_DATE - INTERVAL '5 months')::date, CURRENT_DATE - 1, INTERVAL '1 day') AS gs
    WHERE EXTRACT(ISODOW FROM gs) = 1;

    -- -- Mid-week bursts (consumer #4)
    INSERT INTO public.dataset_query_stats_daily (date, dataset_id, consumer_data_product_id, query_count)
    SELECT gs::date, sales_performance_model_output_port, financial_risk_assessment, 8
    FROM generate_series((CURRENT_DATE - INTERVAL '4 months')::date, CURRENT_DATE - 1, INTERVAL '1 day') AS gs
    WHERE EXTRACT(ISODOW FROM gs) = 3;

    -- ------------------------------------------------------------------------------------------------
    -- START of Insert data quality summary for half of the existing datasets
    -- ------------------------------------------------------------------------------------------------
    WITH dataset_selection AS (
        -- Get up to 20 datasets and assign a row number for variety in data generation
        SELECT id, name, ROW_NUMBER() OVER (ORDER BY id) as rn
        FROM public.datasets
        LIMIT 20
    ),
    summary_generation AS (
        SELECT
            gen_random_uuid() as summary_id,
            id as dataset_id,
            name as dataset_name,
            rn,
            (ARRAY['success', 'failure', 'warning', 'error'])[((rn - 1) % 4) + 1] as status
        FROM dataset_selection
    )
    INSERT INTO public.output_port_data_quality_summaries
        (id, output_port_id, assets_with_checks, assets_with_issues, details_url, description, overall_status, created_at, dimensions)
    SELECT
        summary_id,
        dataset_id,
        10 + rn,
        CASE WHEN status = 'success' THEN 0 ELSE (rn % 3) + 1 END,
        'https://quality-tool.internal/view/' || dataset_id,
        'Recursive CTE generated report for ' || dataset_name,
        status,
        NOW() - (rn || ' hours')::interval,
        json_build_object('validity', lower(status), 'completeness', 'success')
    FROM summary_generation;

    -- 2. Generate the Technical Assets
    WITH dataset_selection AS (
        SELECT id, name, ROW_NUMBER() OVER (ORDER BY id) as rn FROM public.datasets LIMIT 20
        ),
        summary_mapping AS (
    -- We need to join back to the summaries we just created to get the IDs
    SELECT s.id as summary_id, d.name as dataset_name, d.rn
    FROM public.output_port_data_quality_summaries s
        JOIN dataset_selection d ON s.output_port_id = d.id
        )
    INSERT INTO public.data_quality_technical_assets (name, status, data_quality_summary_id)
    SELECT dataset_name || '_table', 'success', summary_id FROM summary_mapping
    UNION ALL
    SELECT dataset_name || '_view', 'warning', summary_id FROM summary_mapping;

    -- ------------------------------------------------------------------------------------------------
    -- Schema objects and properties for output ports
    -- ------------------------------------------------------------------------------------------------

    INSERT INTO public.output_port_schema_objects (id, output_port_id, name, physical_name, logical_type, physical_type, description, position)
    VALUES
        (gen_random_uuid(), sales_performance_model_output_port, 'sales_transactions', 'sales_txn', 'table', 'table', 'Daily sales transaction records per rep and territory', 1),
        (gen_random_uuid(), sales_performance_model_output_port, 'territory_assignments', 'territory_assignments', 'table', 'table', 'Mapping of sales reps to territories and quotas', 2);

    INSERT INTO public.output_port_schema_properties (id, schema_object_id, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    SELECT
        gen_random_uuid(), o.id, p.name, p.business_name, p.logical_type, p.physical_type,
        p.primary_key, p."unique", p.required, p.partitioned, p.partition_key_position, p.primary_key_position,
        p.description, p.examples::jsonb, p.position
    FROM public.output_port_schema_objects o
    JOIN (VALUES
        ('sales_transactions', 'transaction_id',   'Transaction ID',   'string',    'VARCHAR(36)',  true,  true,  true,  false, null, 1, 'Unique transaction identifier',       '["txn-00123"]',   1),
        ('sales_transactions', 'sale_date',         'Sale Date',        'date',      'DATE',         false, false, true,  true,  1,    null,'Date the sale was made',              '["2024-03-15"]',  2),
        ('sales_transactions', 'rep_id',            'Rep ID',           'string',    'VARCHAR(36)',  false, false, true,  false, null, null,'Sales representative identifier',      '["rep-456"]',     3),
        ('sales_transactions', 'territory_code',    'Territory Code',   'string',    'VARCHAR(10)',  false, false, true,  false, null, null,'Geographic territory code',            '["US-WEST-01"]',  4),
        ('sales_transactions', 'product_sku',       'Product SKU',      'string',    'VARCHAR(50)',  false, false, true,  false, null, null,'Stock-keeping unit of the product',   '["SKU-9981"]',    5),
        ('sales_transactions', 'quantity',          'Quantity',         'integer',   'INT',          false, false, true,  false, null, null,'Units sold',                          '[12]',            6),
        ('sales_transactions', 'unit_price',        'Unit Price',       'decimal',   'DECIMAL(10,2)',false, false, true,  false, null, null,'Price per unit at time of sale',      '[49.99]',         7),
        ('sales_transactions', 'discount_pct',      'Discount %',       'decimal',   'DECIMAL(5,2)', false, false, false, false, null, null,'Discount percentage applied',         '[5.0]',           8),
        ('sales_transactions', 'total_amount',      'Total Amount',     'decimal',   'DECIMAL(12,2)',false, false, true,  false, null, null,'Gross sale amount after discount',    '[569.88]',        9),
        ('territory_assignments', 'assignment_id',  'Assignment ID',    'string',    'VARCHAR(36)',  true,  true,  true,  false, null, 1, 'Unique assignment record ID',          '["asgn-001"]',    1),
        ('territory_assignments', 'rep_id',         'Rep ID',           'string',    'VARCHAR(36)',  false, false, true,  false, null, null,'Sales rep identifier',                '["rep-456"]',     2),
        ('territory_assignments', 'territory_code', 'Territory Code',   'string',    'VARCHAR(10)',  false, false, true,  false, null, null,'Territory the rep is assigned to',    '["US-WEST-01"]',  3),
        ('territory_assignments', 'quota_usd',      'Quota (USD)',       'decimal',   'DECIMAL(14,2)',false, false, true,  false, null, null,'Annual revenue quota in USD',         '[250000.00]',     4),
        ('territory_assignments', 'valid_from',     'Valid From',       'date',      'DATE',         false, false, true,  false, null, null,'Start date of assignment',            '["2024-01-01"]',  5),
        ('territory_assignments', 'valid_to',       'Valid To',         'date',      'DATE',         false, false, false, false, null, null,'End date of assignment (null=active)','["2024-12-31"]',  6),
        ('territory_assignments', 'manager_id',     'Manager ID',       'string',    'VARCHAR(36)',  false, false, false, false, null, null,'ID of the territory manager',         '["mgr-012"]',     7)
    ) AS p(schema_name, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    ON o.output_port_id = sales_performance_model_output_port AND o.name = p.schema_name;

    INSERT INTO public.output_port_schema_objects (id, output_port_id, name, physical_name, logical_type, physical_type, description, position)
    VALUES
        (gen_random_uuid(), order_fulfillment_analysis_output_port, 'order_fulfillment_events', 'order_fulfillment_events', 'table', 'table', 'Fulfillment lifecycle events per order line', 1);

    INSERT INTO public.output_port_schema_properties (id, schema_object_id, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    SELECT
        gen_random_uuid(), o.id, p.name, p.business_name, p.logical_type, p.physical_type,
        p.primary_key, p."unique", p.required, p.partitioned, p.partition_key_position, p.primary_key_position,
        p.description, p.examples::jsonb, p.position
    FROM public.output_port_schema_objects o
    JOIN (VALUES
        ('order_fulfillment_events', 'event_id',        'Event ID',         'string',  'VARCHAR(36)',  true,  true,  true,  false, null, 1,   'Unique fulfillment event ID',        '["evt-10001"]',   1),
        ('order_fulfillment_events', 'event_date',       'Event Date',       'date',    'DATE',         false, false, true,  true,  1,    null,'Date the event occurred',           '["2024-04-10"]',  2),
        ('order_fulfillment_events', 'order_id',         'Order ID',         'string',  'VARCHAR(36)',  false, false, true,  false, null, null,'Parent order identifier',            '["ord-88812"]',   3),
        ('order_fulfillment_events', 'order_line_id',    'Order Line ID',    'string',  'VARCHAR(36)',  false, false, true,  false, null, null,'Order line item identifier',         '["line-3"]',      4),
        ('order_fulfillment_events', 'event_type',       'Event Type',       'string',  'VARCHAR(30)',  false, false, true,  false, null, null,'Type: PICKED, PACKED, SHIPPED, etc', '["SHIPPED"]',     5),
        ('order_fulfillment_events', 'warehouse_code',   'Warehouse Code',   'string',  'VARCHAR(10)',  false, false, true,  false, null, null,'Warehouse where event occurred',     '["WH-EU-02"]',    6),
        ('order_fulfillment_events', 'carrier_code',     'Carrier Code',     'string',  'VARCHAR(20)',  false, false, false, false, null, null,'Shipping carrier code',              '["DHL"]',         7),
        ('order_fulfillment_events', 'tracking_number',  'Tracking Number',  'string',  'VARCHAR(50)',  false, false, false, false, null, null,'Carrier tracking number',            '["1Z999AA10123"]',8),
        ('order_fulfillment_events', 'sla_breached',     'SLA Breached',     'boolean', 'BOOLEAN',      false, false, true,  false, null, null,'Whether SLA was breached',           '[false]',         9)
    ) AS p(schema_name, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    ON o.output_port_id = order_fulfillment_analysis_output_port AND o.name = p.schema_name;

    INSERT INTO public.output_port_schema_objects (id, output_port_id, name, physical_name, logical_type, physical_type, description, position)
    VALUES
        (gen_random_uuid(), inventory_management_output_port, 'inventory_snapshots',   'inv_snapshots',   'table', 'Iceberg', 'Daily end-of-day inventory levels per SKU and warehouse', 1),
        (gen_random_uuid(), inventory_management_output_port, 'reorder_recommendations','reorder_recs',    'table', 'Iceberg', 'Automated reorder suggestions based on forecast demand',  2);

    INSERT INTO public.output_port_schema_properties (id, schema_object_id, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    SELECT
        gen_random_uuid(), o.id, p.name, p.business_name, p.logical_type, p.physical_type,
        p.primary_key, p."unique", p.required, p.partitioned, p.partition_key_position, p.primary_key_position,
        p.description, p.examples::jsonb, p.position
    FROM public.output_port_schema_objects o
    JOIN (VALUES
        ('inventory_snapshots', 'snapshot_id',    'Snapshot ID',    'string',  'VARCHAR(36)',  true,  true,  true,  false, null, 1,   'Unique snapshot record ID',           '["snap-20240401-SKU001-WH01"]', 1),
        ('inventory_snapshots', 'snapshot_date',  'Snapshot Date',  'date',    'DATE',         false, false, true,  true,  1,    null,'Date of the inventory snapshot',      '["2024-04-01"]',               2),
        ('inventory_snapshots', 'sku',            'SKU',            'string',  'VARCHAR(50)',  false, false, true,  false, null, null,'Product stock-keeping unit',          '["SKU-1234"]',                 3),
        ('inventory_snapshots', 'warehouse_id',   'Warehouse ID',   'string',  'VARCHAR(36)',  false, false, true,  false, null, null,'Warehouse identifier',                '["WH-EU-01"]',                 4),
        ('inventory_snapshots', 'qty_on_hand',    'Qty On Hand',    'integer', 'INT',          false, false, true,  false, null, null,'Units physically in warehouse',       '[340]',                        5),
        ('inventory_snapshots', 'qty_reserved',   'Qty Reserved',   'integer', 'INT',          false, false, true,  false, null, null,'Units reserved for open orders',      '[80]',                         6),
        ('inventory_snapshots', 'qty_available',  'Qty Available',  'integer', 'INT',          false, false, true,  false, null, null,'Available = on_hand − reserved',      '[260]',                        7),
        ('inventory_snapshots', 'reorder_point',  'Reorder Point',  'integer', 'INT',          false, false, false, false, null, null,'Units level that triggers reorder',   '[100]',                        8),
        ('inventory_snapshots', 'unit_cost',      'Unit Cost',      'decimal', 'DECIMAL(10,2)',false, false, false, false, null, null,'Average unit cost in USD',            '[12.50]',                      9),
        ('reorder_recommendations', 'rec_id',         'Rec ID',         'string',  'VARCHAR(36)',  true,  true,  true,  false, null, 1,   'Recommendation record ID',            '["rec-88711"]',    1),
        ('reorder_recommendations', 'created_date',   'Created Date',   'date',    'DATE',         false, false, true,  true,  1,    null,'Date recommendation was generated',  '["2024-04-02"]',   2),
        ('reorder_recommendations', 'sku',            'SKU',            'string',  'VARCHAR(50)',  false, false, true,  false, null, null,'Product SKU to reorder',              '["SKU-1234"]',     3),
        ('reorder_recommendations', 'warehouse_id',   'Warehouse ID',   'string',  'VARCHAR(36)',  false, false, true,  false, null, null,'Target warehouse',                    '["WH-EU-01"]',     4),
        ('reorder_recommendations', 'suggested_qty',  'Suggested Qty',  'integer', 'INT',          false, false, true,  false, null, null,'Recommended units to order',          '[500]',            5),
        ('reorder_recommendations', 'supplier_id',    'Supplier ID',    'string',  'VARCHAR(36)',  false, false, false, false, null, null,'Preferred supplier identifier',       '["sup-002"]',      6),
        ('reorder_recommendations', 'lead_time_days', 'Lead Time (days)','integer','INT',          false, false, false, false, null, null,'Expected supplier lead time in days', '[7]',              7),
        ('reorder_recommendations', 'status',         'Status',         'string',  'VARCHAR(20)',  false, false, true,  false, null, null,'PENDING, APPROVED, or REJECTED',      '["PENDING"]',      8)
    ) AS p(schema_name, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    ON o.output_port_id = inventory_management_output_port AND o.name = p.schema_name;

    INSERT INTO public.output_port_schema_objects (id, output_port_id, name, physical_name, logical_type, physical_type, description, position)
    VALUES
        (gen_random_uuid(), feature_usage_metrics_daily, 'feature_events',       'feature_events',       'table', 'table', 'Raw feature interaction events emitted by the product', 1),
        (gen_random_uuid(), feature_usage_metrics_daily, 'daily_feature_summary','daily_feature_summary','table', 'table', 'Aggregated daily metrics rolled up from feature_events',2);

    INSERT INTO public.output_port_schema_properties (id, schema_object_id, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    SELECT
        gen_random_uuid(), o.id, p.name, p.business_name, p.logical_type, p.physical_type,
        p.primary_key, p."unique", p.required, p.partitioned, p.partition_key_position, p.primary_key_position,
        p.description, p.examples::jsonb, p.position
    FROM public.output_port_schema_objects o
    JOIN (VALUES
        ('feature_events', 'event_id',       'Event ID',       'string',    'VARCHAR(36)',  true,  true,  true,  false, null, 1,   'Unique event identifier',              '["evt-feats-7712"]', 1),
        ('feature_events', 'event_ts',       'Event Timestamp','timestamp', 'TIMESTAMPTZ',  false, false, true,  true,  1,    null,'UTC timestamp of the event',          '["2024-04-10T14:32:00Z"]', 2),
        ('feature_events', 'user_id',        'User ID',        'string',    'VARCHAR(36)',  false, false, true,  false, null, null,'Authenticated user identifier',        '["usr-334"]',        3),
        ('feature_events', 'session_id',     'Session ID',     'string',    'VARCHAR(36)',  false, false, true,  false, null, null,'Browser or app session ID',            '["sess-9900"]',      4),
        ('feature_events', 'feature_key',    'Feature Key',    'string',    'VARCHAR(100)', false, false, true,  false, null, null,'Identifier of the product feature',    '["dark_mode_toggle"]',5),
        ('feature_events', 'action',         'Action',         'string',    'VARCHAR(30)',  false, false, true,  false, null, null,'User action: CLICK, VIEW, SUBMIT, etc','["CLICK"]',          6),
        ('feature_events', 'platform',       'Platform',       'string',    'VARCHAR(20)',  false, false, true,  false, null, null,'web, ios, or android',                 '["web"]',            7),
        ('feature_events', 'duration_ms',    'Duration (ms)',  'integer',   'INT',          false, false, false, false, null, null,'Time spent on the feature in ms',      '[1240]',             8),
        ('daily_feature_summary', 'summary_id',   'Summary ID',   'string',  'VARCHAR(36)',  true,  true,  true,  false, null, 1,   'Composite PK for the summary row',     '["smry-date-feat"]', 1),
        ('daily_feature_summary', 'summary_date', 'Summary Date', 'date',    'DATE',         false, false, true,  true,  1,    null,'Date of the aggregation window',       '["2024-04-10"]',     2),
        ('daily_feature_summary', 'feature_key',  'Feature Key',  'string',  'VARCHAR(100)', false, false, true,  false, null, null,'Product feature identifier',           '["dark_mode_toggle"]',3),
        ('daily_feature_summary', 'unique_users', 'Unique Users', 'integer', 'INT',          false, false, true,  false, null, null,'Distinct users who triggered feature', '[412]',              4),
        ('daily_feature_summary', 'total_events', 'Total Events', 'integer', 'INT',          false, false, true,  false, null, null,'Total number of events recorded',      '[1803]',             5),
        ('daily_feature_summary', 'avg_duration_ms','Avg Duration (ms)','decimal','DECIMAL(10,2)',false,false,true,false, null, null,'Mean time spent per interaction',      '[980.5]',            6),
        ('daily_feature_summary', 'platform',      'Platform',     'string',  'VARCHAR(20)',  false, false, true,  false, null, null,'Aggregation platform: web/ios/android','["web"]',           7)
    ) AS p(schema_name, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    ON o.output_port_id = feature_usage_metrics_daily AND o.name = p.schema_name;

    INSERT INTO public.output_port_schema_objects (id, output_port_id, name, physical_name, logical_type, physical_type, description, position)
    VALUES
        (gen_random_uuid(), customer_segmentation_weekly_output_port_id, 'customer_segments', 'customer_segments', 'table', 'Parquet', 'Weekly customer segment assignments with RFM scores', 1);

    INSERT INTO public.output_port_schema_properties (id, schema_object_id, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    SELECT
        gen_random_uuid(), o.id, p.name, p.business_name, p.logical_type, p.physical_type,
        p.primary_key, p."unique", p.required, p.partitioned, p.partition_key_position, p.primary_key_position,
        p.description, p.examples::jsonb, p.position
    FROM public.output_port_schema_objects o
    JOIN (VALUES
        ('customer_segments', 'segment_key',       'Segment Key',        'string',  'VARCHAR(36)',  true,  true,  true,  false, null, 1,   'Composite PK: customer_id + week_start',   '["cust-001-2024-W14"]',  1),
        ('customer_segments', 'week_start',         'Week Start',         'date',    'DATE',         false, false, true,  true,  1,    null,'Monday of the ISO week',                  '["2024-04-08"]',         2),
        ('customer_segments', 'customer_id',        'Customer ID',        'string',  'VARCHAR(36)',  false, false, true,  false, null, null,'Customer identifier',                     '["cust-001"]',           3),
        ('customer_segments', 'segment_label',      'Segment',            'string',  'VARCHAR(50)',  false, false, true,  false, null, null,'Assigned segment: Champions, At Risk, etc','["Champions"]',         4),
        ('customer_segments', 'recency_score',      'Recency Score',      'integer', 'SMALLINT',     false, false, true,  false, null, null,'RFM recency score (1-5)',                 '[5]',                    5),
        ('customer_segments', 'frequency_score',    'Frequency Score',    'integer', 'SMALLINT',     false, false, true,  false, null, null,'RFM frequency score (1-5)',               '[4]',                    6),
        ('customer_segments', 'monetary_score',     'Monetary Score',     'integer', 'SMALLINT',     false, false, true,  false, null, null,'RFM monetary score (1-5)',                '[5]',                    7),
        ('customer_segments', 'ltv_usd',            'LTV (USD)',           'decimal', 'DECIMAL(14,2)',false, false, false, false, null, null,'Predicted customer lifetime value',       '[4820.00]',              8),
        ('customer_segments', 'churn_probability',  'Churn Probability',  'decimal', 'DECIMAL(5,4)', false, false, false, false, null, null,'Model-predicted churn probability',       '[0.0321]',               9),
        ('customer_segments', 'preferred_channel',  'Preferred Channel',  'string',  'VARCHAR(20)',  false, false, false, false, null, null,'Most-used contact channel',               '["email"]',              10)
    ) AS p(schema_name, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    ON o.output_port_id = customer_segmentation_weekly_output_port_id AND o.name = p.schema_name;

    INSERT INTO public.output_port_schema_objects (id, output_port_id, name, physical_name, logical_type, physical_type, description, position)
    VALUES
        (gen_random_uuid(), production_planning_insights_forecast, 'production_forecast',    'prod_forecast',    'table', 'Delta Table', 'Rolling 90-day production demand forecast per SKU and plant', 1),
        (gen_random_uuid(), production_planning_insights_forecast, 'capacity_utilization',   'capacity_util',    'table', 'Delta Table', 'Daily plant capacity utilization metrics',                    2);

    INSERT INTO public.output_port_schema_properties (id, schema_object_id, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    SELECT
        gen_random_uuid(), o.id, p.name, p.business_name, p.logical_type, p.physical_type,
        p.primary_key, p."unique", p.required, p.partitioned, p.partition_key_position, p.primary_key_position,
        p.description, p.examples::jsonb, p.position
    FROM public.output_port_schema_objects o
    JOIN (VALUES
        ('production_forecast', 'forecast_id',     'Forecast ID',      'string',  'VARCHAR(36)',  true,  true,  true,  false, null, 1,   'Unique forecast row ID',                '["fcst-sku-plant-date"]',  1),
        ('production_forecast', 'forecast_date',   'Forecast Date',    'date',    'DATE',         false, false, true,  true,  1,    null,'Production date being forecasted',     '["2024-05-01"]',           2),
        ('production_forecast', 'sku',             'SKU',              'string',  'VARCHAR(50)',  false, false, true,  false, null, null,'Product SKU',                           '["SKU-7701"]',             3),
        ('production_forecast', 'plant_id',        'Plant ID',         'string',  'VARCHAR(36)',  false, false, true,  false, null, null,'Manufacturing plant identifier',        '["plant-DE-01"]',          4),
        ('production_forecast', 'forecasted_units','Forecasted Units',  'integer', 'INT',          false, false, true,  false, null, null,'Predicted units to produce',            '[1200]',                   5),
        ('production_forecast', 'confidence_pct',  'Confidence %',     'decimal', 'DECIMAL(5,2)', false, false, true,  false, null, null,'Model confidence (0–100)',              '[87.4]',                   6),
        ('production_forecast', 'raw_material_id', 'Raw Material ID',  'string',  'VARCHAR(36)',  false, false, false, false, null, null,'Primary raw material required',         '["mat-steel-02"]',         7),
        ('production_forecast', 'model_version',   'Model Version',    'string',  'VARCHAR(20)',  false, false, true,  false, null, null,'ML model version used',                 '["v2.3.1"]',               8),
        ('capacity_utilization', 'util_id',         'Util ID',         'string',  'VARCHAR(36)',  true,  true,  true,  false, null, 1,   'Unique utilization record ID',           '["util-plant-date"]',      1),
        ('capacity_utilization', 'util_date',       'Utilization Date','date',    'DATE',         false, false, true,  true,  1,    null,'Date of the measurement',               '["2024-04-15"]',           2),
        ('capacity_utilization', 'plant_id',        'Plant ID',        'string',  'VARCHAR(36)',  false, false, true,  false, null, null,'Manufacturing plant identifier',         '["plant-DE-01"]',          3),
        ('capacity_utilization', 'shift',           'Shift',           'string',  'VARCHAR(10)',  false, false, true,  false, null, null,'Shift: MORNING, AFTERNOON, NIGHT',       '["MORNING"]',              4),
        ('capacity_utilization', 'planned_units',   'Planned Units',   'integer', 'INT',          false, false, true,  false, null, null,'Units planned for the shift',            '[400]',                    5),
        ('capacity_utilization', 'actual_units',    'Actual Units',    'integer', 'INT',          false, false, true,  false, null, null,'Units actually produced',                '[388]',                    6),
        ('capacity_utilization', 'downtime_mins',   'Downtime (mins)', 'integer', 'INT',          false, false, false, false, null, null,'Total unplanned downtime in minutes',    '[18]',                     7),
        ('capacity_utilization', 'oee_pct',         'OEE %',           'decimal', 'DECIMAL(5,2)', false, false, true,  false, null, null,'Overall Equipment Effectiveness score', '[91.2]',                   8)
    ) AS p(schema_name, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    ON o.output_port_id = production_planning_insights_forecast AND o.name = p.schema_name;

    INSERT INTO public.output_port_schema_objects (id, output_port_id, name, physical_name, logical_type, physical_type, description, position)
    VALUES
        (gen_random_uuid(), release_impact_summary, 'release_kpi_snapshots', 'release_kpi_snapshots', 'table', 'Parquet', 'Pre/post KPI snapshots per release version', 1);

    INSERT INTO public.output_port_schema_properties (id, schema_object_id, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    SELECT
        gen_random_uuid(), o.id, p.name, p.business_name, p.logical_type, p.physical_type,
        p.primary_key, p."unique", p.required, p.partitioned, p.partition_key_position, p.primary_key_position,
        p.description, p.examples::jsonb, p.position
    FROM public.output_port_schema_objects o
    JOIN (VALUES
        ('release_kpi_snapshots', 'snapshot_id',      'Snapshot ID',      'string',  'VARCHAR(36)',  true,  true,  true,  false, null, 1,   'Unique snapshot record',              '["snap-v2.4.1-pre"]',  1),
        ('release_kpi_snapshots', 'release_version',  'Release Version',  'string',  'VARCHAR(30)',  false, false, true,  true,  1,    null,'Semver release tag',                 '["v2.4.1"]',           2),
        ('release_kpi_snapshots', 'snapshot_type',    'Snapshot Type',    'string',  'VARCHAR(10)',  false, false, true,  false, null, null,'PRE or POST release',                '["PRE"]',              3),
        ('release_kpi_snapshots', 'snapshot_date',    'Snapshot Date',    'date',    'DATE',         false, false, true,  false, null, null,'Date snapshot was taken',            '["2024-04-01"]',       4),
        ('release_kpi_snapshots', 'error_rate_pct',   'Error Rate %',     'decimal', 'DECIMAL(6,4)', false, false, true,  false, null, null,'API error rate at snapshot time',    '[0.0042]',             5),
        ('release_kpi_snapshots', 'p99_latency_ms',   'P99 Latency (ms)', 'integer', 'INT',          false, false, true,  false, null, null,'99th percentile API latency',        '[312]',                6),
        ('release_kpi_snapshots', 'active_users',     'Active Users',     'integer', 'INT',          false, false, true,  false, null, null,'DAU at snapshot time',               '[14302]',              7),
        ('release_kpi_snapshots', 'conversion_rate',  'Conversion Rate',  'decimal', 'DECIMAL(6,4)', false, false, false, false, null, null,'Checkout conversion rate',           '[0.0381]',             8)
    ) AS p(schema_name, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    ON o.output_port_id = release_impact_summary AND o.name = p.schema_name;

    INSERT INTO public.output_port_schema_objects (id, output_port_id, name, physical_name, logical_type, physical_type, description, position)
    VALUES
        (gen_random_uuid(), release_engagement_by_segment, 'engagement_by_segment', 'engagement_by_segment', 'table', 'Parquet', 'Per-segment engagement metrics broken down by release version', 1);

    release_version_prop_id := gen_random_uuid();

    INSERT INTO public.output_port_schema_properties (id, schema_object_id, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    SELECT
        CASE WHEN p.name = 'release_version' THEN release_version_prop_id ELSE gen_random_uuid() END,
        o.id, p.name, p.business_name, p.logical_type, p.physical_type,
        p.primary_key, p."unique", p.required, p.partitioned, p.partition_key_position, p.primary_key_position,
        p.description, p.examples::jsonb, p.position
    FROM public.output_port_schema_objects o
    JOIN (VALUES
        ('engagement_by_segment', 'row_id',              'Row ID',             'string',  'VARCHAR(36)',  true,  true,  true,  false, null, 1,   'Surrogate key',                       '["rowid-seg-rel"]', 1),
        ('engagement_by_segment', 'release_version',     'Release Version',    'object',  'object',       false, false, true,  true,  1,    null,'Semver release object',               'null',              2),
        ('engagement_by_segment', 'segment_label',       'Segment',            'string',  'VARCHAR(50)',  false, false, true,  false, null, null,'Customer segment name',               '["Champions"]',     3),
        ('engagement_by_segment', 'sessions',            'Sessions',           'integer', 'INT',          false, false, true,  false, null, null,'Number of sessions in window',        '[9812]',            4),
        ('engagement_by_segment', 'avg_session_mins',    'Avg Session (min)',  'decimal', 'DECIMAL(8,2)', false, false, true,  false, null, null,'Mean session duration in minutes',    '[6.4]',             5),
        ('engagement_by_segment', 'feature_adoption_pct','Feature Adoption %', 'decimal', 'DECIMAL(5,2)', false, false, true,  false, null, null,'% of users who used new feature',    '[34.7]',            6),
        ('engagement_by_segment', 'nps_score',           'NPS Score',          'decimal', 'DECIMAL(4,1)', false, false, false, false, null, null,'Net Promoter Score for the segment', '[42.0]',            7),
        ('engagement_by_segment', 'churn_30d_pct',       'Churn 30d %',        'decimal', 'DECIMAL(5,2)', false, false, false, false, null, null,'30-day churn rate post release',      '[2.1]',             8)
    ) AS p(schema_name, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    ON o.output_port_id = release_engagement_by_segment AND o.name = p.schema_name;

    INSERT INTO public.output_port_schema_properties (id, schema_object_id, parent_property_id, name, business_name, logical_type, physical_type, required, primary_key, "unique", partitioned, description, examples, position)
    VALUES
        (gen_random_uuid(), (SELECT schema_object_id FROM public.output_port_schema_properties WHERE id = release_version_prop_id), release_version_prop_id, 'major_version', 'Major Version', 'integer', 'INT',     true,  false, false, false, 'Breaking-change version number', '[2]',  1),
        (gen_random_uuid(), (SELECT schema_object_id FROM public.output_port_schema_properties WHERE id = release_version_prop_id), release_version_prop_id, 'minor_version', 'Minor Version', 'integer', 'INT',     true,  false, false, false, 'Backwards-compatible feature number', '[4]',  2),
        (gen_random_uuid(), (SELECT schema_object_id FROM public.output_port_schema_properties WHERE id = release_version_prop_id), release_version_prop_id, 'hotfix_version','Hotfix Version','integer', 'INT',     true,  false, false, false, 'Patch / hotfix number',         '[1]',  3);

    INSERT INTO public.output_port_schema_objects (id, output_port_id, name, physical_name, logical_type, physical_type, description, position)
    VALUES
        (gen_random_uuid(), margin_trends_by_product, 'product_margin_monthly', 'product_margin_monthly', 'table', 'Delta Table', 'Monthly gross and net margin per product line',          1),
        (gen_random_uuid(), margin_trends_by_product, 'cost_breakdown',          'cost_breakdown',          'table', 'Delta Table', 'Cost component breakdown: COGS, fulfillment, overhead', 2);

    INSERT INTO public.output_port_schema_properties (id, schema_object_id, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    SELECT
        gen_random_uuid(), o.id, p.name, p.business_name, p.logical_type, p.physical_type,
        p.primary_key, p."unique", p.required, p.partitioned, p.partition_key_position, p.primary_key_position,
        p.description, p.examples::jsonb, p.position
    FROM public.output_port_schema_objects o
    JOIN (VALUES
        ('product_margin_monthly', 'margin_key',        'Margin Key',       'string',  'VARCHAR(36)',  true,  true,  true,  false, null, 1,   'PK: product_id + month',                '["prod-001-2024-04"]',  1),
        ('product_margin_monthly', 'month_start',       'Month Start',      'date',    'DATE',         false, false, true,  true,  1,    null,'First day of the reporting month',     '["2024-04-01"]',        2),
        ('product_margin_monthly', 'product_id',        'Product ID',       'string',  'VARCHAR(36)',  false, false, true,  false, null, null,'Product identifier',                   '["prod-001"]',          3),
        ('product_margin_monthly', 'product_line',      'Product Line',     'string',  'VARCHAR(50)',  false, false, true,  false, null, null,'Product line / category',              '["Enterprise SaaS"]',   4),
        ('product_margin_monthly', 'revenue_usd',       'Revenue (USD)',     'decimal', 'DECIMAL(14,2)',false, false, true,  false, null, null,'Total revenue for the month',          '[182000.00]',           5),
        ('product_margin_monthly', 'cogs_usd',          'COGS (USD)',        'decimal', 'DECIMAL(14,2)',false, false, true,  false, null, null,'Cost of goods sold',                  '[62000.00]',            6),
        ('product_margin_monthly', 'gross_margin_pct',  'Gross Margin %',   'decimal', 'DECIMAL(6,2)', false, false, true,  false, null, null,'(Revenue - COGS) / Revenue × 100',    '[65.93]',               7),
        ('product_margin_monthly', 'net_margin_pct',    'Net Margin %',     'decimal', 'DECIMAL(6,2)', false, false, false, false, null, null,'After-overhead net margin percentage', '[31.20]',               8),
        ('cost_breakdown', 'breakdown_id',   'Breakdown ID',   'string',  'VARCHAR(36)',  true,  true,  true,  false, null, 1,   'Unique cost breakdown record',          '["bd-prod-001-2024-04"]', 1),
        ('cost_breakdown', 'month_start',    'Month Start',    'date',    'DATE',         false, false, true,  true,  1,    null,'First day of the reporting month',     '["2024-04-01"]',           2),
        ('cost_breakdown', 'product_id',     'Product ID',     'string',  'VARCHAR(36)',  false, false, true,  false, null, null,'Product identifier',                   '["prod-001"]',             3),
        ('cost_breakdown', 'cost_category',  'Cost Category',  'string',  'VARCHAR(30)',  false, false, true,  false, null, null,'COGS, FULFILLMENT, OVERHEAD, OTHER',   '["COGS"]',                 4),
        ('cost_breakdown', 'amount_usd',     'Amount (USD)',   'decimal', 'DECIMAL(14,2)',false, false, true,  false, null, null,'Cost amount in USD',                   '[62000.00]',               5),
        ('cost_breakdown', 'cost_driver',    'Cost Driver',    'string',  'VARCHAR(100)', false, false, false, false, null, null,'Free-text label for the cost driver',  '["Cloud hosting fees"]',  6),
        ('cost_breakdown', 'variance_usd',   'Variance (USD)', 'decimal', 'DECIMAL(14,2)',false, false, false, false, null, null,'Delta vs prior month',                 '[1200.00]',                7)
    ) AS p(schema_name, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    ON o.output_port_id = margin_trends_by_product AND o.name = p.schema_name;

    INSERT INTO public.output_port_schema_objects (id, output_port_id, name, physical_name, logical_type, physical_type, description, position)
    VALUES
        (gen_random_uuid(), user_feedback_insights_report, 'feedback_analysis', 'feedback_analysis', 'table', 'Parquet', 'NLP-enriched user feedback records with sentiment and topic tags', 1);

    INSERT INTO public.output_port_schema_properties (id, schema_object_id, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    SELECT
        gen_random_uuid(), o.id, p.name, p.business_name, p.logical_type, p.physical_type,
        p.primary_key, p."unique", p.required, p.partitioned, p.partition_key_position, p.primary_key_position,
        p.description, p.examples::jsonb, p.position
    FROM public.output_port_schema_objects o
    JOIN (VALUES
        ('feedback_analysis', 'feedback_id',      'Feedback ID',      'string',  'VARCHAR(36)',  true,  true,  true,  false, null, 1,   'Unique feedback record',               '["fb-77123"]',         1),
        ('feedback_analysis', 'submitted_date',   'Submitted Date',   'date',    'DATE',         false, false, true,  true,  1,    null,'Date feedback was submitted',          '["2024-04-09"]',       2),
        ('feedback_analysis', 'user_id',          'User ID',          'string',  'VARCHAR(36)',  false, false, false, false, null, null,'User identifier (nullable = anonymous)','["usr-334"]',         3),
        ('feedback_analysis', 'channel',          'Channel',          'string',  'VARCHAR(20)',  false, false, true,  false, null, null,'Feedback channel: in-app, email, etc',  '["in-app"]',          4),
        ('feedback_analysis', 'raw_text',         'Raw Text',         'string',  'TEXT',         false, false, true,  false, null, null,'Original feedback text',               '["Love the new UI!"]', 5),
        ('feedback_analysis', 'sentiment',        'Sentiment',        'string',  'VARCHAR(10)',  false, false, true,  false, null, null,'POSITIVE, NEUTRAL, or NEGATIVE',       '["POSITIVE"]',        6),
        ('feedback_analysis', 'sentiment_score',  'Sentiment Score',  'decimal', 'DECIMAL(4,3)', false, false, true,  false, null, null,'Sentiment confidence (0–1)',            '[0.921]',             7),
        ('feedback_analysis', 'topics',           'Topics',           'array',   'JSONB',        false, false, false, false, null, null,'Extracted topic labels',               '[["UX","Performance"]]',8),
        ('feedback_analysis', 'csat_score',       'CSAT Score',       'integer', 'SMALLINT',     false, false, false, false, null, null,'Customer satisfaction score (1–5)',     '[5]',                 9)
    ) AS p(schema_name, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    ON o.output_port_id = user_feedback_insights_report AND o.name = p.schema_name;

    INSERT INTO public.output_port_schema_objects (id, output_port_id, name, physical_name, logical_type, physical_type, description, position)
    VALUES
        (gen_random_uuid(), feature_usage_metrics_weekly, 'weekly_feature_summary', 'weekly_feature_summary', 'table', 'Delta Table', 'Weekly rollup of feature engagement aggregated from daily data', 1);

    INSERT INTO public.output_port_schema_properties (id, schema_object_id, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    SELECT
        gen_random_uuid(), o.id, p.name, p.business_name, p.logical_type, p.physical_type,
        p.primary_key, p."unique", p.required, p.partitioned, p.partition_key_position, p.primary_key_position,
        p.description, p.examples::jsonb, p.position
    FROM public.output_port_schema_objects o
    JOIN (VALUES
        ('weekly_feature_summary', 'week_key',        'Week Key',         'string',  'VARCHAR(36)',  true,  true,  true,  false, null, 1,   'PK: feature_key + week_start',          '["dark_mode-2024-W14"]',  1),
        ('weekly_feature_summary', 'week_start',      'Week Start',       'date',    'DATE',         false, false, true,  true,  1,    null,'Monday of the ISO week',               '["2024-04-08"]',          2),
        ('weekly_feature_summary', 'feature_key',     'Feature Key',      'string',  'VARCHAR(100)', false, false, true,  false, null, null,'Product feature identifier',           '["dark_mode_toggle"]',    3),
        ('weekly_feature_summary', 'unique_users',    'Unique Users',     'integer', 'INT',          false, false, true,  false, null, null,'Distinct weekly active users',         '[2901]',                  4),
        ('weekly_feature_summary', 'total_events',    'Total Events',     'integer', 'INT',          false, false, true,  false, null, null,'Total events across all days',         '[12430]',                 5),
        ('weekly_feature_summary', 'avg_daily_users', 'Avg Daily Users',  'decimal', 'DECIMAL(10,2)',false, false, true,  false, null, null,'Mean daily unique users',              '[414.4]',                 6),
        ('weekly_feature_summary', 'retention_pct',   'Retention %',      'decimal', 'DECIMAL(5,2)', false, false, false, false, null, null,'% of users returning in the same week','[68.3]',                  7),
        ('weekly_feature_summary', 'top_platform',    'Top Platform',     'string',  'VARCHAR(20)',  false, false, false, false, null, null,'Platform with most usage: web/ios/android','["web"]',             8)
    ) AS p(schema_name, name, business_name, logical_type, physical_type, primary_key, "unique", required, partitioned, partition_key_position, primary_key_position, description, examples, position)
    ON o.output_port_id = feature_usage_metrics_weekly AND o.name = p.schema_name;

end $$;
