do $$
declare
    -- DOMAINS
    hr_id uuid;
    sales_id uuid;
    marketing_id uuid;
    manufacturing_id uuid;

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

    -- DATA PRODUCTS
    sales_funnel_optimization_id uuid;
    customer_segmentation_id uuid;
    marketing_campaign_id uuid;
    sales_forecast_id uuid;

    -- DATASETS
    customer_data_id uuid;
    sales_data_id uuid;
    products_data_id uuid;
    stores_data_id uuid;
    employees_data_id uuid;

    -- PLATFORMS
    returned_platform_id uuid;
    s3_service_id uuid;
    glue_service_id uuid;
    returned_environment_id_dev uuid;
    returned_environment_id_prd uuid;
    databricks_id uuid;
    databricks_service_id uuid;
    snowflake_id uuid;
    snowflake_service_id uuid;
    redshift_service_id uuid;

    -- DATA OUTPUTS
    glue_configuration_id uuid;
    glue_data_output_id uuid;
    databricks_configuration_id uuid;
    databricks_data_output_id uuid;

    product_owner_id uuid;
    admin_role_id uuid;
    product_member_id uuid;
    dataset_owner_id uuid;
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

    -- PLATFORMS
    SELECT id FROM public.platforms WHERE name = 'AWS' INTO returned_platform_id;
    SELECT id FROM public.platform_services WHERE platform_id = returned_platform_id AND name = 'S3' INTO s3_service_id;
    SELECT id FROM public.platform_services WHERE platform_id = returned_platform_id AND name = 'Glue' INTO glue_service_id;

    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('6bd82fd6-9a23-4517-a07c-9110d83ab38f', returned_platform_id, s3_service_id, '["datalake","ingress","egress"]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('fa026b3a-7a17-4c32-b279-995af021f6c2', returned_platform_id, glue_service_id, '["clean","master"]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.platforms (id, "name") VALUES ('9be7613c-42fb-4b93-952d-1874ed1ddf77', 'Snowflake') returning id INTO snowflake_id;
    INSERT INTO public.platform_services (id, "name", platform_id, result_string_template, technical_info_template) VALUES ('a75189c1-fa42-4980-9497-4bea4c968a5b', 'Snowflake', snowflake_id, '{database}.{schema}.{table}', '{database}.{schema}.{table}') returning id INTO snowflake_service_id;
    INSERT INTO public.platform_services (id, "name", platform_id, result_string_template, technical_info_template) VALUES ('de328223-fd90-4170-a7a1-376e4ebe0594', 'Redshift', returned_platform_id,'{database}__{schema}.{table}', '{database}__{schema}.{table}') returning id INTO redshift_service_id;
    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('e5f82cba-28fd-4895-b8b2-4b31cba06cde', snowflake_id, snowflake_service_id, '["clean","master"]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('9ff4c542-c3fb-43cd-982e-f6bd20d24f7f', returned_platform_id, redshift_service_id, '["clean","master"]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.platforms (id, "name") VALUES ('baa5c47b-805a-4cbb-ad8b-038c66e81b7e', 'Databricks') returning id INTO databricks_id;
    INSERT INTO public.platform_services (id, "name", platform_id, result_string_template, technical_info_template) VALUES ('ce208413-b629-44d2-9f98-e5b47a315a56', 'Databricks', databricks_id, '{catalog}.{schema}.{table}', '{catalog}.{schema}.{table}') returning id INTO databricks_service_id;
    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('0b9a0e7f-8fee-4fd3-97e0-830e1612b77a', databricks_id, databricks_service_id, '["clean","master"]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- ENVIRONMENTS
    INSERT INTO public.environments ("name", acronym, context, is_default, created_on, updated_on, deleted_at) VALUES ('development', 'dev', 'dev_context', true, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO returned_environment_id_dev;
    INSERT INTO public.environments ("name", acronym, context, is_default, created_on, updated_on, deleted_at) VALUES ('production', 'prd', 'prd_context', false, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO returned_environment_id_prd;
    INSERT INTO public.env_platform_configs (id, environment_id, platform_id, "config", created_on, updated_on, deleted_at) VALUES('f8d7e6c5-b4a3-492d-8c1b-9a0b8c7d6e5f', returned_environment_id_dev, databricks_id, '{"account_id":"012345678901","metastore_id":"012345678901","credential_name":"dbx-uc-access", "workspace_urls": {"7d9ec9fd-89cf-477e-b077-4c8d1a3ce3cc": "databricks_prd_link1", "bd09093e-14ff-41c1-b74d-7c2ce9821d1c":"databricks_prd_link2"}}', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_configs (id, environment_id, platform_id, "config", created_on, updated_on, deleted_at) VALUES('a9b8c7d6-e5f4-483e-9d2c-1b3a4c5d6e7f', returned_environment_id_prd, databricks_id, '{"account_id":"012345678901","metastore_id":"012345678901","credential_name":"dbx-uc-access", "workspace_urls": {"7d9ec9fd-89cf-477e-b077-4c8d1a3ce3cc": "databricks_dev_link1", "bd09093e-14ff-41c1-b74d-7c2ce9821d1c":"databricks_dev_link2"}}', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_configs (id, environment_id, platform_id, "config", created_on, updated_on, deleted_at) VALUES ('6abc7055-20e8-4475-a228-d43b719d316f', returned_environment_id_dev, snowflake_id, '{"account_id": "012345678901", "region": "eu-west-1", "can_read_from": ["production"], "login_url":""}', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_configs (id, environment_id, platform_id, "config", created_on, updated_on, deleted_at) VALUES ('ae064d40-53ec-45aa-b456-caa653de970a', returned_environment_id_prd, snowflake_id, '{"account_id": "012345678901", "region": "eu-west-1", "can_read_from": [], "login_url":""}', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_configs (id, environment_id, platform_id, "config", created_on, updated_on, deleted_at) VALUES ('daa8e3e8-1485-4eb2-8b4b-575e8d10a570', returned_environment_id_dev, returned_platform_id, '{"account_id": "012345678901", "region": "eu-west-1", "can_read_from": ["production"]}', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_configs (id, environment_id, platform_id, "config", created_on, updated_on, deleted_at) VALUES ('e2aa2f6d-585f-4b43-8ea4-982b7bab0142', returned_environment_id_prd, returned_platform_id, '{"account_id": "012345678901", "region": "eu-west-1", "can_read_from": []}', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('93f4b677-5ae8-450d-91a6-e15196b2e774', returned_environment_id_dev, returned_platform_id, s3_service_id, '[{"identifier":"datalake","bucket_name":"datalake_bucket_dev","bucket_arn":"datalake_bucket_arn_dev","kms_key_arn":"datalake_kms_key_dev","is_default":true},{"identifier":"ingress","bucket_name":"ingress_bucket_dev","bucket_arn":"ingress_bucket_arn_dev","kms_key_arn":"ingress_kms_key_dev","is_default":false},{"identifier":"egress","bucket_name":"egress_bucket_dev","bucket_arn":"egress_bucket_arn_dev","kms_key_arn":"egress_kms_key_dev","is_default":false}]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('9c1d025c-f342-4665-8461-ba8b9f4035ff', returned_environment_id_prd, returned_platform_id, s3_service_id, '[{"identifier":"datalake","bucket_name":"datalake_bucket_prd","bucket_arn":"datalake_bucket_arn_prd","kms_key_arn":"datalake_kms_key_prd","is_default":true},{"identifier":"ingress","bucket_name":"ingress_bucket_prd","bucket_arn":"ingress_bucket_arn_prd","kms_key_arn":"ingress_kms_key_prd","is_default":false},{"identifier":"egress","bucket_name":"egress_bucket_prd","bucket_arn":"egress_bucket_arn_prd","kms_key_arn":"egress_kms_key_prd","is_default":false}]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('1c52b0e5-961f-412a-995e-0c1efae19f41', returned_environment_id_dev, returned_platform_id, glue_service_id, '[{"identifier":"clean_test","database_name":"clean_test_dev","bucket_identifier":"datalake","s3_path":"clean/test"},{"identifier":"master_test","database_name":"master_test_dev","bucket_identifier":"datalake","s3_path":"master/test"}]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('ba42ca59-ab5d-498e-8cd0-cdd680f80bb0', returned_environment_id_prd, returned_platform_id, glue_service_id, '[{"identifier":"clean_test","database_name":"clean_test_prd","bucket_identifier":"datalake","s3_path":"clean/test"},{"identifier":"master_test","database_name":"master_test_prd","bucket_identifier":"datalake","s3_path":"master/test"}]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('c45661de-29a1-4562-9183-e7162cfa3503', returned_environment_id_dev, returned_platform_id, redshift_service_id, '[{"identifier":"clean","database_name":"clean_dev","bucket_identifier":"datalake","s3_path":"clean/"},{"identifier":"master","database_name":"master_dev","bucket_identifier":"datalake","s3_path":"master"}]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('5d0506f4-5e7a-45df-a1e8-108fda00d194', returned_environment_id_prd, returned_platform_id, redshift_service_id, '[{"identifier":"clean","database_name":"clean_prd","bucket_identifier":"datalake","s3_path":"clean/"},{"identifier":"master","database_name":"master_prd","bucket_identifier":"datalake","s3_path":"master"}]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('f8d7e6c5-b4a3-492d-8c1b-9a0b8c7d6e5f', returned_environment_id_dev, databricks_id, databricks_service_id, '[]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('a9b8c7d6-e5f4-483e-9d2c-1b3a4c5d6e7f', returned_environment_id_prd, databricks_id, databricks_service_id, '[]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- DOMAINS
    INSERT INTO public.domains (id, "name", description, created_on, updated_on, deleted_at) VALUES ('672debaf-31f9-4233-820b-ad2165af044e', 'HR', 'Human Resources', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO hr_id;
    INSERT INTO public.domains (id, "name", description, created_on, updated_on, deleted_at) VALUES ('bd09093e-14ff-41c1-b74d-7c2ce9821d1c', 'Sales', 'Sales', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO sales_id;
    INSERT INTO public.domains (id, "name", description, created_on, updated_on, deleted_at) VALUES ('7d9ec9fd-89cf-477e-b077-4c8d1a3ce3cc', 'Marketing', 'Marketing', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO marketing_id;
    INSERT INTO public.domains (id, "name", description, created_on, updated_on, deleted_at) VALUES ('623e6fbf-3a06-434e-995c-b0336e71806e', 'Manufacturing', 'Manufacturing', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO manufacturing_id;

    -- DATA PRODUCT TYPES
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('90ab1128-329f-47dd-9420-c9681bfc68c4', 'Processing', 'Processing', 'PROCESSING', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO processing_type_id;
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('1b4a64b3-96fb-404c-a73c-294802dc9852', 'Reporting', 'Reporting', 'REPORTING', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO reporting_type_id;
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('74b13338-aa85-4552-8ccb-7d51550c67de', 'Exploration', 'Exploration', 'EXPLORATION', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO exploration_type_id;
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('c25cf2c2-418a-4d1d-a975-c6af61161546', 'Ingestion', 'Ingestion', 'INGESTION', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO ingestion_type_id;
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('f1672c38-ad1a-401a-8dd3-e0b026ab1416', 'Machine Learning', 'Machine Learning', 'MACHINE_LEARNING', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO machine_learning_type_id;
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('3c289333-2d55-4aed-8bd5-85015a1567fe', 'Analytics', 'Analytics', 'ANALYTICS', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO analytics_type_id;

    -- USERS
    INSERT INTO public.users (email, id, external_id, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('alice.baker@gmail.com', 'a02d3714-97e3-40d8-92b7-3b018fd1229f', 'alice.baker@gmail.com', 'Alice', 'Baker', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO alice_id;
    INSERT INTO public.users (email, id, external_id, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('bob.baker@gmail.com', '35f2dd11-3119-4eb3-8f19-01b323131221', 'bob.baker@gmail.com', 'Bob', 'Baker', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO bob_id;
    INSERT INTO public.users (email, id, external_id, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('jane.doe@dataminded.com', 'd9f3aae2-391e-46c1-aec6-a7ae1114a7da', 'jane.doe@dataminded.com', 'Jane', 'Doe', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO jane_id;
    INSERT INTO public.users (email, id, external_id, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('john.doe@dataminded.com', 'b72fca38-17ff-4259-a075-5aaa5973343c', 'john.doe@dataminded.com', 'John', 'Doe', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO john_id;

    -- ROLES
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('f80c101c-345c-4d5b-9524-57c55bd12d2d', 'Everyone', 'global', 1, 'This is the role that is used as fallback for users that don''t have another role', ARRAY [102, 103, 104, 105], timezone('utc'::text, CURRENT_TIMESTAMP + INTERVAL '1 seconds'), NULL, NULL);
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('e43b6f7a-e776-49b2-9b51-117d8644d971', 'Owner', 'data_product', 2, 'The owner of a Data Product', ARRAY [301, 302, 304, 305, 306, 307, 308, 309, 310, 311, 313, 314, 315], timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into product_owner_id;
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('18e67286-92aa-449a-ba46-ac26eb0de21d', 'Solution Architect', 'data_product', 0, 'The Solution Architect for a Data Product', ARRAY [303, 309, 310, 311, 312, 313, 314], timezone('utc'::text, CURRENT_TIMESTAMP + INTERVAL '1 seconds'), NULL, NULL);
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('9ca3bfdd-2919-4190-a8bb-55e9ee7d70dd', 'Member', 'data_product', 0, 'A regular team member of a Data Product', ARRAY [313, 314, 315], timezone('utc'::text, CURRENT_TIMESTAMP + INTERVAL '2 seconds'), NULL, NULL) returning id into product_member_id;
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('9a9d7deb-14d9-4257-a986-7900aa70ef8f', 'Owner', 'dataset', 2, 'The owner of a Dataset', ARRAY [401, 402, 404, 405, 406, 407, 408, 411, 412, 413], timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into dataset_owner_id;
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('2ae1b4e3-5b13-491a-912b-984e2e90b858', 'Solution Architect', 'dataset', 0, 'The Solution Architect for a Dataset', ARRAY [403, 409, 410], timezone('utc'::text, CURRENT_TIMESTAMP + INTERVAL '1 seconds'), NULL, NULL);
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at) VALUES ('db8d7a76-c50b-4e95-8549-8da86f48e7c2', 'Member', 'dataset', 0, 'A regular team member of a Dataset', ARRAY [413], timezone('utc'::text, CURRENT_TIMESTAMP + INTERVAL '2 seconds'), NULL, NULL);
    INSERT INTO public.roles (id, name, scope, prototype, description, permissions, created_on, updated_on, deleted_at)
    VALUES
        ('00000000-0000-0000-0000-000000000000', 'Admin', 'global', 3, 'Global admin role', ARRAY[]::integer[], timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL)
    RETURNING id INTO admin_role_id;

    -- DATA PRODUCTS
    INSERT INTO public.data_products (id, "name", namespace, description, about, status, type_id, domain_id, created_on, updated_on, deleted_at) VALUES ('e269fd59-14f4-4710-9ce0-bb31b1c8b541', 'Sales Funnel Optimization', 'sales_funnel_optimization', 'Analyze data to optimize the Sales Funnel', '<h2>Sales Funnel Optimization</h2><p></p><p>This data product aims to analyze the current sales funnel, identify drop-off points,  implement improvements, and test new strategies.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li><p>Increase Conversion Rates</p></li><li><p>Enhance Lead Quality</p></li><li><p>Optimize Lead Nurturing Processes</p></li><li><p>Improve Sales Team Efficiency</p></li><li><p>Maximize Customer Lifetime Value (CLV)</p></li><li><p>Data-Driven Decision Making</p></li><li><p>Align Marketing and Sales Efforts</p></li><li><p>Enhance Customer Experience</p></li><li><p>Drive Revenue Growth</p></li></ul>', 'ACTIVE', exploration_type_id, sales_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO sales_funnel_optimization_id;
    INSERT INTO public.data_products (id, "name", namespace, description, about, status, type_id, domain_id, created_on, updated_on, deleted_at) VALUES ('ffcf5286-8f14-4411-8dfe-75dc7ed9ec36', 'Consumer Analysis', 'consumer_analysis', 'Customer Segmentation and Targeting', '<h2>Consumer Analysis</h2><p></p><p>This data product aims to develop cutting-edge AI models for analyzing consumer behaviour. </p><p>By leveraging deep learning techniques, we strive to automate the analysis of consumer data, enabling more personalized targeting and customer retention.</p><p></p><p><strong>Primary benefits include:</strong></p><ul><li><p>Enhanced Personalization</p></li><li><p>Improved Customer Retention</p></li><li><p>Efficient Resource Allocation</p></li><li><p>Better Decision-Making</p></li></ul>', 'ACTIVE', analytics_type_id, marketing_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO customer_segmentation_id;
    INSERT INTO public.data_products (id, "name", namespace, description, about, status, type_id, domain_id, created_on, updated_on, deleted_at) VALUES ('55394c2e-8d33-4397-a388-20338ff87c0a', 'Digital Marketing Data Ingestion', 'digital_marketing', 'Ingest data to support digital marketing', '<h2>Digital Marketing Data Ingestion</h2><p></p><p>This data product focuses on ingesting all data needed to support our Digital Marketing campaigns.</p><p></p><p><strong>Core goals are:</strong></p><ul><li><p>Data Source Identification and Integration</p></li><li><p>Data Cleaning and Transformation</p></li><li><p>Data Enrichment and Enhancement</p></li><li><p>Real-time and Batch Processing</p></li><li><p>Data Governance and Security</p></li><li><p>Automation and Scalability</p></li><li><p>Collaboration and Stakeholder Engagement</p></li></ul>', 'ACTIVE', ingestion_type_id, marketing_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO marketing_campaign_id;
    INSERT INTO public.data_products (id, "name", namespace, description, about, status, type_id, domain_id, created_on, updated_on, deleted_at) VALUES ('4c3f686f-13ec-41c0-a31c-60a19f05bbe5', 'Sales Forecast', 'sales_forecast', 'Develop predictive models for sales forecasting', '<h2>Sales Forecast</h2><p></p><p>This data product focuses on developing predictive models for forecasting sales. By leveraging advanced analytics and machine learning, we aim to forecast sales results based on an extensive list of parameters.</p><p></p><p><strong>Strategic aims are:</strong></p><ul><li><p>Accurate Sales Predictions</p></li><li><p>Demand Planning and Inventory Management</p></li><li><p>Resource Allocation and Operational Efficiency</p></li><li><p>Strategic Decision Support</p></li><li><p>Risk Management and Scenario Planning</p></li><li><p>Performance Monitoring and KPI Tracking</p></li><li><p>Continuous Improvement and Innovation</p></li><li><p>Cross-functional Collaboration</p></li></ul>', 'PENDING', machine_learning_type_id, sales_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO sales_forecast_id;

    -- DATASETS
    INSERT INTO public.datasets (id, namespace, "name", description, about, status, access_type, domain_id, created_on, updated_on, deleted_at) VALUES ('a1804479-c376-49cf-8970-29ec0ee0bc91', 'customer_data', 'Customer Data', 'Customer detail data from CRM, POS, loyalty programs, feedback systems, surveys, ...', '<h2>Customer Detail Data</h2><p></p><p>This dataset contains customer data obtained from various sources (CRM, POS, loyalty programs, feedback systems, surveys, …).</p><p></p><p><strong>Key components include:</strong></p><ul><li><p>Customer Demographics</p></li><li><p>Customer Segmentation Data</p></li><li><p>Purchase History</p></li><li><p>Behavioral Data</p></li><li><p>Customer Feedback</p></li><li><p>Loyalty Program Data</p></li><li><p>Customer Service Interactions</p></li></ul>', 'PENDING', 'RESTRICTED', marketing_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO customer_data_id;
    INSERT INTO public.datasets (id, namespace, "name", description, about, status, access_type, domain_id, created_on, updated_on, deleted_at) VALUES ('590da97a-a689-4d1f-adf4-27d1f3fa28e8', 'sales_data', 'Sales', 'Sales detail data from POS, E- Commerce, OMS, accounting and billing, ...', '<h2>Sales Data</h2><p></p><p>This dataset contains sales data obtained from various sources (POS, E- Commerce, OMS, accounting and billing, …).</p><p></p><p><strong>Key components include:</strong></p><ul><li><p>Transaction Information</p></li><li><p>Product Details</p></li><li><p>Customer Information</p></li><li><p>Sales Representative Information</p></li><li><p>Location Details</p></li><li><p>Payment Information</p></li><li><p>Discounts and Promotions</p></li><li><p>Return and Refund Information</p></li></ul>', 'ACTIVE', 'PUBLIC', sales_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO sales_data_id;
    INSERT INTO public.datasets (id, namespace, "name", description, about, status, access_type, domain_id, created_on, updated_on, deleted_at) VALUES ('e4621c2e-4855-44d0-924f-5f77d3860ae4', 'products_data', 'Products', 'Products detail data from PIM, ERP, ERP, Supply Chain Management, ...', '<h2>Products Data</h2><p></p><p>This dataset contains products data obtained from various sources (Product Information Management, ERP, Supply Chain Management, Third Party vendors, …).</p><p></p><p><strong>Key components include:</strong></p><ul><li><p>Product Identification</p></li><li><p>Product Attributes</p></li><li><p>Product Specifications</p></li><li><p>Product Images and Media</p></li><li><p>Pricing and Inventory</p></li><li><p>Sales and Marketing</p></li><li><p>Logistics and Fulfillment</p></li><li><p>Compliance and Regulatory Information</p></li><li><p>Customer Support</p></li></ul>', 'ACTIVE', 'PUBLIC', manufacturing_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO products_data_id;
    INSERT INTO public.datasets (id, namespace, "name", description, about, status, access_type, domain_id, created_on, updated_on, deleted_at) VALUES ('cf6c98ae-44c2-4c63-90ff-0a8d6ec90f19', 'stores_data', 'Stores', 'Stores detail data from ERP, CRM, POS, ...', '<h2>Stores Data</h2><p></p><p>This dataset contains stores data obtained from various sources (ERP, CRM, POS, …).</p><p></p><p><strong>Key components include:</strong></p><ul><li><p>Store Identification</p></li><li><p>Location Information</p></li><li><p>Contact Details</p></li><li><p>Operating Hours</p></li><li><p>Store Facilities</p></li><li><p>Product Offering</p></li><li><p>Services Offered</p></li><li><p>Operational Details</p></li><li><p>Sales Performance</p></li></ul>', 'ACTIVE', 'PUBLIC', sales_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO stores_data_id;
    INSERT INTO public.datasets (id, namespace, "name", description, about, status, access_type, domain_id, created_on, updated_on, deleted_at) VALUES ('4cd6e3d7-129f-496b-a9e5-c6fbdbc024e5', 'employees_data', 'Employee Data', 'Employee detail data from HRIS, Payroll,  Timesheets, ...', '<h2>Employee Data</h2><p></p><p>This dataset contains employee data obtained from various sources (HRIS, Payroll,  Timesheets, …).</p><p></p><p><strong>Key components include:</strong></p><ul><li><p>Personal Information</p></li><li><p>Employment Details</p></li><li><p>Compensation and Benefits</p></li><li><p>Time and Attendance</p></li><li><p>Performance Data</p></li><li><p>Training and Development</p></li><li><p>Engagement and Feedback</p></li><li><p>Compliance and Legal</p></li><li><p>IT and System Access</p></li></ul>', 'PENDING', 'RESTRICTED', hr_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO employees_data_id;

    -- DATA PRODUCTS - DATASETS
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('0658e52e-b69e-4787-b7b1-df215d75329c', sales_funnel_optimization_id, sales_data_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('8c9ae075-aac3-47f3-b46f-1e7d66ea008a', sales_funnel_optimization_id, stores_data_id, 'PENDING', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('9cc43cb5-f943-4f4e-8b41-8001fd33a0a0', sales_funnel_optimization_id, customer_data_id, 'APPROVED', bob_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('7df30caf-d2a7-4a39-b528-45a1aed7b4c0', sales_funnel_optimization_id, products_data_id, 'APPROVED', bob_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('f5923c52-d89e-429d-b2f2-ad8eb431a85e', customer_segmentation_id, sales_data_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('c18ade7a-ef72-4da3-957d-60b750a21538', customer_segmentation_id, customer_data_id, 'PENDING', alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('e27d437d-ba3c-4633-a5c3-95474fbc61ca', marketing_campaign_id, customer_data_id, 'PENDING', alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('24bf3a56-e48e-45de-a193-2164d0992b09', sales_forecast_id, sales_data_id, 'APPROVED', bob_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('0ab77909-c839-4048-8005-4f5604c6fa5e', sales_forecast_id, customer_data_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('96f62e70-e8d8-44b3-9303-e8e387a404b0', sales_forecast_id, products_data_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- DATA OUTPUTS
    INSERT INTO public.data_output_configurations (id, configuration_type, bucket_identifier, "database", database_suffix, "table", table_path, database_path, created_on, updated_on, deleted_at) VALUES ('b6bc5710-8706-45fb-bf85-6ed90d8a7428', 'GlueDataOutput', 'datalake', 'digital_marketing', 'glue_output', '*', '*', 'digital_marketing', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into glue_configuration_id;
    INSERT INTO public.data_outputs (id, configuration_id, "name", namespace, description, status, owner_id, platform_id, service_id, created_on, updated_on, deleted_at) VALUES ('4d35e5ef-6205-4d4d-aec1-a9456b3a3ba6', glue_configuration_id, 'Marketing Glue table', 'marketing-glue-table', 'A Glue table containing marketing data', 'ACTIVE', marketing_campaign_id,returned_platform_id, glue_service_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO glue_data_output_id;
    INSERT INTO public.data_output_configurations (id, configuration_type, bucket_identifier, "catalog", schema, catalog_path, table_path, "table", created_on, updated_on, deleted_at) VALUES ('cdd627e5-08b2-4dc8-add6-32ff569f543b', 'DatabricksDataOutput', 'datalake', 'digital_marketing', 'databricks_output', '', '', 'digital_marketing', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into databricks_configuration_id;
    INSERT INTO public.data_outputs (id, configuration_id, "name", namespace, description, status, owner_id, platform_id, service_id, created_on, updated_on, deleted_at) VALUES ('4bbe93f4-3514-4839-a705-6532a6cb041f', databricks_configuration_id, 'Marketing Databricks table', 'marketing-databricks-table', 'A Databricks table containing marketing data', 'ACTIVE', marketing_campaign_id,databricks_id, databricks_service_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO databricks_data_output_id;

    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('90238525-841a-4e50-9387-9dc8ebbf8fe8', databricks_data_output_id, sales_data_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('6c2ea4b3-48af-448d-9e9e-2892d3dddf50', glue_data_output_id, sales_data_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    INSERT INTO public.data_product_settings (id, namespace, name, "default", "order", type, tooltip, category, scope) VALUES ('e12ec335-d7a4-4e27-8225-b66da70f3158', 'iam_role', 'IAM service accounts', 'false', '100', 'CHECKBOX', 'Generate IAM access credentials for this data product', 'AWS', 'DATAPRODUCT');

    -- -- INSERT ROLE ASSIGNMENTS FOR DATA PRODUCTS
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_on, decided_on, decided_by_id)
    VALUES
        -- Sales Funnel Optimization
        ('46060c7b-ad7c-4405-aa7b-e5f0aa0b61ae', sales_funnel_optimization_id, john_id, product_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('cbf9b323-c37d-44c4-a88f-05657c393f57', sales_funnel_optimization_id, bob_id, product_member_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('6afe2dc4-c59d-4a7e-9f63-05813190041b', sales_funnel_optimization_id, alice_id, product_member_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('b9206f00-dfad-4813-a531-7777097f6f40', sales_funnel_optimization_id, jane_id, product_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),

        -- Customer Segmentation
        ('9dcb7545-3d82-4230-aa45-f99724a45f77', customer_segmentation_id, john_id, product_member_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('3d6c1f8c-0d57-4aaa-b2e0-79dfff456dce', customer_segmentation_id, bob_id, product_member_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('135b71f6-4836-4f84-91c9-35fc1dda3781', customer_segmentation_id, alice_id, product_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('310e9de4-0218-4167-b0b4-378f4a53d51f', customer_segmentation_id, jane_id, product_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),

        -- Marketing Campaign
        ('97ac436c-598b-4fe9-a25a-1f9da2b348b2', marketing_campaign_id, john_id, product_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('d4dc3e0e-8316-4f27-a377-15276d33541b', marketing_campaign_id, bob_id, product_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('b1f839de-8e36-4e5f-817d-6ff247d15b0e', marketing_campaign_id, alice_id, product_member_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('f90a21f1-49f1-42ee-a310-fbeb95993c90', marketing_campaign_id, jane_id, product_member_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),

        -- Sales Forecast
        ('db656db9-0d9c-4740-9cc3-b6ac6e05c634', sales_forecast_id, john_id, product_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('7a0c32aa-0082-4b88-b5db-8a50443d9556', sales_forecast_id, bob_id, product_member_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('3841cd2a-bcf7-4720-952e-4995d330d743', sales_forecast_id, alice_id, product_member_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id);

    -- INSERT ROLE ASSIGNMENTS FOR DATASETS
INSERT INTO public.role_assignments_dataset (id, dataset_id, user_id, role_id, decision, requested_on, decided_on, decided_by_id)
VALUES
    -- Customer Data
    ('773c12c0-ec70-4178-b387-9a87ba0a9dbc', customer_data_id, john_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
    ('2c686614-7986-4cac-a96c-62551ffafb4c', customer_data_id, jane_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),

    -- Stores Data
    ('8ffa9aa9-35bf-4815-8843-e8833999c764', stores_data_id, john_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
    ('8ca03984-dda3-4b11-9bea-3c69fc4d2414', stores_data_id, bob_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
    ('882d12a5-58f2-41d3-8064-97631b153492', stores_data_id, jane_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),

    -- Sales Data
    ('ac0db781-60c2-4d7e-92d1-4fbb0b6c9133', sales_data_id, bob_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
    ('ce9bdf7e-8fb4-49c9-af05-be618f26b2f7', sales_data_id, jane_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),

    -- Products Data
    ('c6ccef1f-ba1a-4dc5-b0c4-5a2b8a9fd265', products_data_id, alice_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),

    -- Employees Data
    ('e790b201-4275-4c01-aeac-a632ce773454', employees_data_id, jane_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id);

-- INSERT ROLE ASSIGNMENTS FOR GLOBAL ROLES
INSERT INTO public.role_assignments_global (id, user_id, role_id, decision, requested_on, decided_on, decided_by_id)
VALUES
    ('f2d1fc47-3afa-49be-b652-fa6de00bea6b', john_id, admin_role_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
    ('b8288793-ae92-4808-9927-d3da20d1321b', jane_id, admin_role_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id);
end $$;
