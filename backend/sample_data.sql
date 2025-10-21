do $$
declare
    -- DOMAINS
    hr_id uuid;
    clinical_id uuid;
    proteomics_id uuid;
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
    rnd_program_pipeline_id uuid;
    ai_model_histology_images_id uuid;
    demand_forecast_id uuid;
    prediction_model_id uuid;

    -- DATASETS
    histology_rnd_dataset_id uuid;
    histology_clinical_dataset_id uuid;
    drug_pipeline_dataset_id uuid;
    demand_forecast_dataset_id uuid;
    proteomics_dataset_id uuid;

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

    -- ...existing platform configuration code...
    INSERT INTO public.platforms (id, "name") VALUES ('9be7613c-42fb-4b93-952d-1874ed1ddf77', 'Snowflake') returning id INTO snowflake_id;
    INSERT INTO public.platforms (id, "name") VALUES ('6be7613c-42fb-4b93-952d-1874ed1ddf76', 'Conveyor');
    INSERT INTO public.platform_services (id, "name", platform_id, result_string_template, technical_info_template) VALUES ('a75189c1-fa42-4980-9497-4bea4c968a5b', 'Snowflake', snowflake_id, '{database}.{schema}.{table}', '{database}.{schema}.{table}') returning id INTO snowflake_service_id;
    INSERT INTO public.platform_services (id, "name", platform_id, result_string_template, technical_info_template) VALUES ('de328223-fd90-4170-a7a1-376e4ebe0594', 'Redshift', returned_platform_id,'{database}__{schema}.{table}', '{database}__{schema}.{table}') returning id INTO redshift_service_id;
    INSERT INTO public.platforms (id, "name") VALUES ('baa5c47b-805a-4cbb-ad8b-038c66e81b7e', 'Databricks') returning id INTO databricks_id;
    INSERT INTO public.platform_services (id, "name", platform_id, result_string_template, technical_info_template) VALUES ('ce208413-b629-44d2-9f98-e5b47a315a56', 'Databricks', databricks_id, '{catalog}.{schema}.{table}', '{catalog}.{schema}.{table}') returning id INTO databricks_service_id;

    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('6bd82fd6-9a23-4517-a07c-9110d83ab38f', returned_platform_id, s3_service_id, '["datalake","ingress","egress"]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('fa026b3a-7a17-4c32-b279-995af021f6c2', returned_platform_id, glue_service_id, '["clean","master"]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.platform_service_configs (id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('0b9a0e7f-8fee-4fd3-97e0-830e1612b77a', databricks_id, databricks_service_id, '["clean","master"]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('90ab1128-329f-47dd-9420-c9681bfc68c4', 'Processing', 'Processing', 'PROCESSING', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO processing_type_id;
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('1b4a64b3-96fb-404c-a73c-294802dc9852', 'Reporting', 'Reporting', 'REPORTING', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO reporting_type_id;
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('74b13338-aa85-4552-8ccb-7d51550c67de', 'Exploration', 'Exploration', 'EXPLORATION', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO exploration_type_id;
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('c25cf2c2-418a-4d1d-a975-c6af61161546', 'Ingestion', 'Ingestion', 'INGESTION', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO ingestion_type_id;
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('f1672c38-ad1a-401a-8dd3-e0b026ab1416', 'Machine Learning', 'Machine Learning', 'MACHINE_LEARNING', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO machine_learning_type_id;
    INSERT INTO public.data_product_types (id, "name", description, icon_key, created_on, updated_on, deleted_at) VALUES ('3c289333-2d55-4aed-8bd5-85015a1567fe', 'Analytics', 'Analytics', 'ANALYTICS', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO analytics_type_id;

    -- ...existing platform service configs...
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

    -- ENVIRONMENTS
    INSERT INTO public.environments ("name", context, acronym, is_default, created_on, updated_on, deleted_at) VALUES ('development', 'arn:aws:iam::130966031144:role/cvr-pbac-iam-{{}}-dev-demo', 'dev', true, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO returned_environment_id_dev;
    INSERT INTO public.environments ("name", context, acronym, is_default, created_on, updated_on, deleted_at) VALUES ('production', 'arn:aws:iam::130966031144:role/cvr-pbac-iam-{{}}-prd-demo', 'prd', false, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO returned_environment_id_prd;

    INSERT INTO public.env_platform_configs (id, environment_id, platform_id, "config", created_on, updated_on, deleted_at) VALUES ('daa8e3e8-1485-4eb2-8b4b-575e8d10a570', returned_environment_id_dev, returned_platform_id, '{"account_id": "130966031144", "region": "eu-west-1", "can_read_from": ["production"]}', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_configs (id, environment_id, platform_id, "config", created_on, updated_on, deleted_at) VALUES ('e2aa2f6d-585f-4b43-8ea4-982b7bab0142', returned_environment_id_prd, returned_platform_id, '{"account_id": "130966031144", "region": "eu-west-1", "can_read_from": []}', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('93f4b677-5ae8-450d-91a6-e15196b2e774', returned_environment_id_dev, returned_platform_id, s3_service_id, '[{"identifier":"datalake","bucket_name":"cvr-pbac-s3-datalake-dev-demo-eqpkja","bucket_arn":"arn:aws:s3:::cvr-pbac-s3-datalake-dev-demo-eqpkja","kms_key_arn":"arn:aws:kms:eu-west-1:130966031144:key/9cfae60f-63cb-46ea-83fb-d39df661f8d1","is_default":true},{"identifier":"ingress","bucket_name":"cvr-pbac-s3-ingress-dev-demo-yikcsx","bucket_arn":"arn:aws:s3:::cvr-pbac-s3-ingress-dev-demo-yikcsx","kms_key_arn":"arn:aws:kms:eu-west-1:130966031144:key/7d8dffe2-0958-406d-b069-011b5c257e97","is_default":false},{"identifier":"egress","bucket_name":"cvr-pbac-s3-egress-dev-demo-bugfma","bucket_arn":"arn:aws:s3:::cvr-pbac-s3-egress-dev-demo-bugfma","kms_key_arn":"arn:aws:kms:eu-west-1:130966031144:key/01182b9c-2f70-4000-94a1-171daf3be5ba","is_default":false}]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('9c1d025c-f342-4665-8461-ba8b9f4035ff', returned_environment_id_prd, returned_platform_id, s3_service_id, '[{"identifier":"datalake","bucket_name":"cvr-pbac-s3-datalake-prd-demo-tqzddc","bucket_arn":"arn:aws:s3:::cvr-pbac-s3-datalake-prd-demo-tqzddc","kms_key_arn":"arn:aws:kms:eu-west-1:130966031144:key/8a6736dc-3fd5-471a-9dd0-f0faeecf1ec6","is_default":true},{"identifier":"ingress","bucket_name":"cvr-pbac-s3-ingress-prd-demo-cubodu","bucket_arn":"arn:aws:s3:::cvr-pbac-s3-ingress-prd-demo-cubodu","kms_key_arn":"arn:aws:kms:eu-west-1:130966031144:key/b00aa784-3f1b-424f-9b6a-5bce746adb83","is_default":false},{"identifier":"egress","bucket_name":"cvr-pbac-s3-egress-prd-demo-dfxalw","bucket_arn":"arn:aws:s3:::cvr-pbac-s3-egress-prd-demo-dfxalw","kms_key_arn":"arn:aws:kms:eu-west-1:130966031144:key/ba3de25b-2798-43e9-84c6-64267107a82b","is_default":false}]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('1c52b0e5-961f-412a-995e-0c1efae19f41', returned_environment_id_dev, returned_platform_id, glue_service_id, '[{"identifier":"clean_test","database_name":"clean_test_dev","bucket_identifier":"datalake","s3_path":"clean/test"},{"identifier":"master_test","database_name":"master_test_dev","bucket_identifier":"datalake","s3_path":"master/test"}]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.env_platform_service_configs (id, environment_id, platform_id, service_id, "config", created_on, updated_on, deleted_at) VALUES('ba42ca59-ab5d-498e-8cd0-cdd680f80bb0', returned_environment_id_prd, returned_platform_id, glue_service_id, '[{"identifier":"clean_test","database_name":"clean_test_prd","bucket_identifier":"datalake","s3_path":"clean/test"},{"identifier":"master_test","database_name":"master_test_prd","bucket_identifier":"datalake","s3_path":"master/test"}]', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- DOMAINS
    INSERT INTO public.domains (id, "name", description, created_on, updated_on, deleted_at) VALUES ('672debaf-31f9-4233-820b-ad2165af044e', 'HR', 'Human Resources', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO hr_id;
    INSERT INTO public.domains (id, "name", description, created_on, updated_on, deleted_at) VALUES ('bd09093e-14ff-41c1-b74d-7c2ce9821d1c', 'Clinical', 'Clinical Research and Development', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO clinical_id;
    INSERT INTO public.domains (id, "name", description, created_on, updated_on, deleted_at) VALUES ('7d9ec9fd-89cf-477e-b077-4c8d1a3ce3cc', 'Proteomics', 'Proteomics and Biomarker Discovery', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO proteomics_id;
    INSERT INTO public.domains (id, "name", description, created_on, updated_on, deleted_at) VALUES ('623e6fbf-3a06-434e-995c-b0336e71806e', 'Manufacturing', 'Manufacturing and Supply Chain', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO manufacturing_id;

    -- DATA PRODUCT TYPES
    -- ...existing data product types code...

    -- USERS
    INSERT INTO public.users (email, id, external_id, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('alice.baker@pharma.com', 'a02d3714-97e3-40d8-92b7-3b018fd1229f', 'alice.baker@pharma.com', 'Alice', 'Baker', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO alice_id;
    INSERT INTO public.users (email, id, external_id, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('bob.johnson@pharma.com', '35f2dd11-3119-4eb3-8f19-01b323131221', 'bob.johnson@pharma.com', 'Bob', 'Johnson', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO bob_id;
    INSERT INTO public.users (email, id, external_id, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('jane.researcher@pharma.com', 'd9f3aae2-391e-46c1-aec6-a7ae1114a7da', 'jane.researcher@pharma.com', 'Jane', 'Researcher', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO jane_id;
    INSERT INTO public.users (email, id, external_id, first_name, last_name, created_on, updated_on, deleted_at) VALUES ('john.scientist@pharma.com', 'b72fca38-17ff-4259-a075-5aaa5973343c', 'john.scientist@pharma.com', 'John', 'Scientist', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO john_id;

    -- ROLES
    -- ...existing roles code...

    -- DATA PRODUCTS
    INSERT INTO public.data_products (id, "name", namespace, description, about, status, type_id, domain_id, created_on, updated_on, deleted_at) VALUES ('9e76db57-a057-447d-9b6d-f3ecad35f775', 'R&D Program Pipeline', 'portal-rdprogram', 'Manage and track R&D programs and drug pipeline', '<h2>R&D Program Pipeline</h2><p></p><p>This data product aims to streamline the management and tracking of R&D programs and drug pipeline. It provides a centralized platform for monitoring the progress of drug candidates from discovery to clinical trials.</p><p></p><p><strong>Key objectives include:</strong></p><ul><li>Centralized management of R&D programs</li><li>Real-time tracking of drug pipeline progress</li><li>Enhanced collaboration among stakeholders</li></ul>', 'ACTIVE', exploration_type_id, clinical_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO rnd_program_pipeline_id;
    INSERT INTO public.data_products (id, "name", namespace, description, about, status, type_id, domain_id, created_on, updated_on, deleted_at) VALUES ('e811a336-48ec-423f-ba6b-f9d0465c305f', 'AI Model for Histology Images', 'portal-aimodel', 'Develop AI models for analyzing histology images', '<h2>AI Model for Histology Images</h2><p></p><p>This data product aims to develop cutting-edge AI models for analyzing histology images. By leveraging deep learning techniques, we strive to automate the analysis of histology slides, enabling faster and more accurate diagnosis and research.</p><p></p><p><strong>Primary targets include:</strong></p><ul><li>Automation of histology slide analysis</li><li>Improvement in diagnostic speed and accuracy</li><li>Facilitation of research through AI-driven insights</li></ul>', 'ACTIVE', analytics_type_id, proteomics_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO ai_model_histology_images_id;
    INSERT INTO public.data_products (id, "name", namespace, description, about, status, type_id, domain_id, created_on, updated_on, deleted_at) VALUES ('10e11a46-5062-4847-8622-a621aa0fcd14', 'Demand and Forecast', 'portal-demandandforecast', 'Develop models for demand forecasting and planning', '<h2>Demand and Forecast</h2><p></p><p>This data product focuses on developing advanced models for demand forecastingand planning. By leveraging historical data and machine learning techniques, we aim to improve the accuracy of demand predictions and optimize inventory management.</p><p></p><p><strong>Core goals are:</strong></p><ul><li>Predictive modeling for accurate demand forecasting</li><li>Optimization of inventory levels and supply chain efficiency</li><li>Integration of machine learning for improved prediction accuracy</li></ul>', 'ACTIVE', ingestion_type_id, proteomics_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO demand_forecast_id;
    INSERT INTO public.data_products (id, "name", namespace, description, about, status, type_id, domain_id, created_on, updated_on, deleted_at) VALUES ('b76ccd64-6725-4969-9393-c2f492602cc5', 'Prediction Model', 'portal-prediction', 'Develop predictive models for various business areas', '<h2>Prediction Model</h2><p></p><p>This data product focuses on developing predictive models for various businessareas, such as clinical trials, manufacturing, and commercial operations. By leveraging advanced analytics and machine learning, we aim to improve decision-making and optimize processes across the organization.</p><p></p><p><strong>Strategic aims are:</strong></p><ul><li>Development of predictive models for key business areas</li><li>Enhancement of operational efficiency through data-driven decisions</li><li>Support for strategic planning and risk management</li></ul>', 'PENDING', machine_learning_type_id, clinical_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO prediction_model_id;

    -- DATASETS
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, domain_id, created_on, updated_on, deleted_at) VALUES ('bdad0dec-19e6-4c85-a655-0960ca3a484c', 'histology_rnd_dataset', ai_model_histology_images_id, 'Histology RnD Data', 'Histology data from R&D experiments', '<h2>Histology RnD Data</h2><p></p><p>This dataset contains histology data from R&D experiments,including images of tissue samples, clinical data, and experimental results. The data is used for research and development purposes, such as biomarker discovery and drug development. <p></p><p><strong>Key features include:</strong></p><ul><li>Images of tissue samples from clinical trials</li><li>Clinical data and patient information</li><li>Experimental results and analysis</li></ul>', 'ACTIVE', 'RESTRICTED', proteomics_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO histology_rnd_dataset_id;
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, domain_id, created_on, updated_on, deleted_at) VALUES ('dfbedc22-8295-4b35-a0fe-6b06c12adfde', 'histology_clinical_dataset', ai_model_histology_images_id, 'Histology Clinical Data', 'Histology data from clinical trials', '<h2>Histology Clinical Data</h2><p></p><p>This dataset contains histology data from clinical trials,including images of tissue samples, clinical data, and experimental results. The data is used for research and development purposes, such as biomarker discovery and drug development.</p><p></p><p><strong>Key features include:</strong></p><ul><li>Images of tissue samples from clinical trials</li><li>Clinical data and patient information</li><li>Experimental results and analysis</li></ul>', 'ACTIVE', 'PUBLIC', clinical_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO histology_clinical_dataset_id;
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, domain_id, created_on, updated_on, deleted_at) VALUES ('5abfe489-8b84-4843-9582-84fbbc019556', 'drug_pipeline_dataset', rnd_program_pipeline_id, 'Drug Pipeline Data', 'Data related to drug pipeline and development', '<h2>Drug Pipeline Data</h2><p></p><p>This dataset contains data related to drug pipeline and development,including information on drug candidates, clinical trials, and regulatory requirements. The data is used for research and development purposes, such as monitoring the progress of drug candidates and optimizing clinical trials.</p><p></p><p><strong>Key features include:</strong></p><ul><li><p>Information on drug candidates and development stages</p></li><li><p>Clinical trial data and results</p></li><li><p>Regulatory requirements and compliance</p></li></ul>', 'PENDING', 'RESTRICTED', manufacturing_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO drug_pipeline_dataset_id;
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, domain_id, created_on, updated_on, deleted_at) VALUES ('1b5f0d56-0699-42ce-a407-f47df844b0e2', 'demand_forecast_dataset', ai_model_histology_images_id, 'Demand Forecast Data', 'Historical data for demand forecasting', '<h2>Demand Forecast Data</h2><p></p><p>This dataset contains historical data for demand forecasting,including sales data, market trends, and customer behavior. The data is used for research and development purposes, such as developing models for demand forecasting and planning.</p><p></p><p><strong>Essential components are:</strong></p><ul><li>Sales figures across different markets</li><li>Analysis of consumer purchasing patterns</li><li>Insights into emerging market trends</li></ul>', 'ACTIVE', 'PUBLIC', clinical_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO demand_forecast_dataset_id;
    INSERT INTO public.datasets (id, namespace, data_product_id, "name", description, about, status, access_type, domain_id, created_on, updated_on, deleted_at) VALUES ('ae895c51-3c32-49b9-bd54-2fa4e04c6cc8', 'proteomics_dataset', prediction_model_id, 'Proteomics Data', 'Proteomics data for biomarker discovery', '<h2>Proteomics Data</h2><p></p><p>This dataset contains proteomics data for biomarker discovery, including protein expression data, mass spectrometry results, and clinical data. The data is used for research and development purposes, such as identifying biomarkers for disease diagnosis and treatment.</p><p></p><p><strong>Important elements include:</strong></p><ol><li>Quantitative protein expression levels</li><li>Mass spectrometry data for protein identification</li><li>Clinical correlations for biomarker validation</li></ol>', 'PENDING', 'PUBLIC', hr_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO proteomics_dataset_id;

    -- DATA PRODUCTS - DATASETS
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('0658e52e-b69e-4787-b7b1-df215d75329c', rnd_program_pipeline_id, drug_pipeline_dataset_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('8c9ae075-aac3-47f3-b46f-1e7d66ea008a', rnd_program_pipeline_id, histology_clinical_dataset_id, 'PENDING', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('9cc43cb5-f943-4f4e-8b41-8001fd33a0a0', ai_model_histology_images_id, histology_rnd_dataset_id, 'APPROVED', bob_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('f5923c52-d89e-429d-b2f2-ad8eb431a85e', demand_forecast_id, demand_forecast_dataset_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('c18ade7a-ef72-4da3-957d-60b750a21538', demand_forecast_id, proteomics_dataset_id, 'PENDING', alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('e27d437d-ba3c-4633-a5c3-95474fbc61ca', prediction_model_id, histology_clinical_dataset_id, 'PENDING', alice_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('24bf3a56-e48e-45de-a193-2164d0992b09', prediction_model_id, demand_forecast_dataset_id, 'APPROVED', bob_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_products_datasets (id, data_product_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('0ab77909-c839-4048-8005-4f5604c6fa5e', prediction_model_id, proteomics_dataset_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    -- DATA OUTPUTS
    INSERT INTO public.data_output_configurations (id, configuration_type, bucket_identifier, "database", database_suffix, "table", table_path, database_path, created_on, updated_on, deleted_at) VALUES ('b6bc5710-8706-45fb-bf85-6ed90d8a7428', 'GlueDataOutput', 'datalake', 'pharma_research', 'glue_output', '*', '*', 'pharma_research', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into glue_configuration_id;
    INSERT INTO public.data_outputs (id, configuration_id, "name", namespace, description, status, owner_id, platform_id, service_id, created_on, updated_on, deleted_at) VALUES ('4d35e5ef-6205-4d4d-aec1-a9456b3a3ba6', glue_configuration_id, 'Pharma Research Glue table', 'pharma-research-glue-table', 'A Glue table containing pharmaceutical research data', 'ACTIVE', ai_model_histology_images_id,returned_platform_id, glue_service_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO glue_data_output_id;
    INSERT INTO public.data_output_configurations (id, configuration_type, bucket_identifier, "catalog", schema, catalog_path, table_path, "table", created_on, updated_on, deleted_at) VALUES ('cdd627e5-08b2-4dc8-add6-32ff569f543b', 'DatabricksDataOutput', 'datalake', 'pharma_research', 'databricks_output', '', '', 'pharma_research', timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id into databricks_configuration_id;
    INSERT INTO public.data_outputs (id, configuration_id, "name", namespace, description, status, owner_id, platform_id, service_id, created_on, updated_on, deleted_at) VALUES ('4bbe93f4-3514-4839-a705-6532a6cb041f', databricks_configuration_id, 'Pharma Research Databricks table', 'pharma-research-databricks-table', 'A Databricks table containing pharmaceutical research data', 'ACTIVE', ai_model_histology_images_id,databricks_id, databricks_service_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL) returning id INTO databricks_data_output_id;

    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('90238525-841a-4e50-9387-9dc8ebbf8fe8', databricks_data_output_id, histology_clinical_dataset_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);
    INSERT INTO public.data_outputs_datasets (id, data_output_id, dataset_id, status, requested_by_id, requested_on, approved_by_id, approved_on, denied_by_id, denied_on, created_on, updated_on, deleted_at) VALUES ('6c2ea4b3-48af-448d-9e9e-2892d3dddf50', glue_data_output_id, demand_forecast_dataset_id, 'APPROVED', john_id, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL, NULL, NULL, timezone('utc'::text, CURRENT_TIMESTAMP), NULL, NULL);

    INSERT INTO public.data_product_settings (id, namespace, name, "default", "order", type, tooltip, category, scope) VALUES ('e12ec335-d7a4-4e27-8225-b66da70f3158', 'iam_role', 'IAM service accounts', 'false', '100', 'CHECKBOX', 'Generate IAM access credentials for this data product', 'AWS', 'DATAPRODUCT');

    -- INSERT ROLE ASSIGNMENTS FOR DATA PRODUCTS
    INSERT INTO public.role_assignments_data_product (id, data_product_id, user_id, role_id, decision, requested_on, decided_on, decided_by_id)
    VALUES
        -- R&D Program Pipeline
        ('46060c7b-ad7c-4405-aa7b-e5f0aa0b61ae', rnd_program_pipeline_id, john_id, product_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('cbf9b323-c37d-44c4-a88f-05657c393f57', rnd_program_pipeline_id, bob_id, product_member_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('6afe2dc4-c59d-4a7e-9f63-05813190041b', rnd_program_pipeline_id, alice_id, product_member_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('b9206f00-dfad-4813-a531-7777097f6f40', rnd_program_pipeline_id, jane_id, product_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),

        -- AI Model for Histology Images
        ('9dcb7545-3d82-4230-aa45-f99724a45f77', ai_model_histology_images_id, john_id, product_member_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('3d6c1f8c-0d57-4aaa-b2e0-79dfff456dce', ai_model_histology_images_id, bob_id, product_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('135b71f6-4836-4f84-91c9-35fc1dda3781', ai_model_histology_images_id, alice_id, product_member_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('310e9de4-0218-4167-b0b4-378f4a53d51f', ai_model_histology_images_id, jane_id, product_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),

        -- Demand and Forecast
        ('97ac436c-598b-4fe9-a25a-1f9da2b348b2', demand_forecast_id, john_id, product_member_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('d4dc3e0e-8316-4f27-a377-15276d33541b', demand_forecast_id, bob_id, product_member_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('b1f839de-8e36-4e5f-817d-6ff247d15b0e', demand_forecast_id, alice_id, product_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('f90a21f1-49f1-42ee-a310-fbeb95993c90', demand_forecast_id, jane_id, product_member_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),

        -- Prediction Model
        ('db656db9-0d9c-4740-9cc3-b6ac6e05c634', prediction_model_id, john_id, product_member_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('7a0c32aa-0082-4b88-b5db-8a50443d9556', prediction_model_id, bob_id, product_member_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('3841cd2a-bcf7-4720-952e-4995d330d743', prediction_model_id, alice_id, product_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id);

    -- INSERT ROLE ASSIGNMENTS FOR DATASETS
    INSERT INTO public.role_assignments_dataset (id, dataset_id, user_id, role_id, decision, requested_on, decided_on, decided_by_id)
    VALUES
        -- Histology R&D Dataset
        ('773c12c0-ec70-4178-b387-9a87ba0a9dbc', histology_rnd_dataset_id, john_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('2c686614-7986-4cac-a96c-62551ffafb4c', histology_rnd_dataset_id, jane_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),

        -- Histology Clinical Dataset
        ('8ffa9aa9-35bf-4815-8843-e8833999c764', histology_clinical_dataset_id, john_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('8ca03984-dda3-4b11-9bea-3c69fc4d2414', histology_clinical_dataset_id, bob_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('882d12a5-58f2-41d3-8064-97631b153492', histology_clinical_dataset_id, jane_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),

        -- Drug Pipeline Dataset
        ('ac0db781-60c2-4d7e-92d1-4fbb0b6c9133', drug_pipeline_dataset_id, bob_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('ce9bdf7e-8fb4-49c9-af05-be618f26b2f7', drug_pipeline_dataset_id, jane_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),

        -- Demand Forecast Dataset
        ('c6ccef1f-ba1a-4dc5-b0c4-5a2b8a9fd265', demand_forecast_dataset_id, alice_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),

        -- Proteomics Dataset
        ('e790b201-4275-4c01-aeac-a632ce773454', proteomics_dataset_id, jane_id, dataset_owner_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id);

    -- INSERT ROLE ASSIGNMENTS FOR GLOBAL ROLES
    INSERT INTO public.role_assignments_global (id, user_id, role_id, decision, requested_on, decided_on, decided_by_id)
    VALUES
        ('f2d1fc47-3afa-49be-b652-fa6de00bea6b', john_id, admin_role_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id),
        ('b8288793-ae92-4808-9927-d3da20d1321b', jane_id, admin_role_id, 'APPROVED', timezone('utc'::text, CURRENT_TIMESTAMP), timezone('utc'::text, CURRENT_TIMESTAMP), john_id);
end $$;
