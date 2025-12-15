# Data Products

# Manual initialization

- `poetry run dbt init NAME --skip-profile-setup`
- Create `profiles.yml` within the folder

# Running the dataproduct

- `poetry run dbt run --project-dir sales_crm_customers --profiles-dir sales_crm_customers`
- `poetry run dbt run --project-dir sales_erp_orders --profiles-dir sales_erp_orders`
- `poetry run dbt run --project-dir logistics_wms_shipments --profiles-dir logistics_wms_shipments`

# Demo case

- `poetry run dbt run --project-dir marketing_customer_360 --profiles-dir marketing_customer_360`
