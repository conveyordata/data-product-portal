# Provisioner Routes Documentation

## Overview

The provisioner handles webhooks from the Data Product Portal to automate:
- Project scaffolding
- S3 storage setup
- Access control management

## Registered Routes

### 1. Create Data Product
**Route:** `POST /api/data_products`
**Handler:** `handle_create_data_product(payload)`

**Triggered when:** A new data product is created in the portal

**Actions:**
1. Fetch data product details from portal API
2. Create S3 bucket (if not exists) and prefix for the namespace
3. Generate S3 credentials (currently returns minioadmin for demo)
4. Scaffold SQLMesh project using cookiecutter template
5. Write `.env` file with S3 configuration
6. Make `run.sh` executable
7. Update data product lifecycle to "Ready"
8. Create PostgreSQL output port (optional)

**Example payload:**
```json
{
  "method": "POST",
  "url": "/api/data_products",
  "response": "{\"id\":\"uuid-here\",\"namespace\":\"my-product\"}"
}
```

**Result:**
- New project at `/products/{namespace}/`
- S3 prefix created: `s3://data-products/{namespace}/`
- Working SQLMesh project with example models

---

### 2. Approve Input Port (Grant Consumer Access)
**Route:** `POST /api/v2/data_products/{provider_id}/output_ports/{output_port_id}/input_ports/approve`
**Handler:** `handle_approve_link(provider_id, output_port_id, payload)`

**Triggered when:** An access request (input port) is approved in the portal

**Actions:**
1. Check response status code (only proceeds if 200)
2. Extract `consuming_data_product_id` from request body
3. Fetch provider data product details → get provider namespace
4. Fetch consumer data product details → get consumer namespace
5. Log S3 access grant (provider → consumer)
6. Create `ACCESSIBLE_DATA_PRODUCTS.txt` in consumer project documenting the access

**Example payload:**
```json
{
  "method": "POST",
  "url": "/api/v2/data_products/provider-uuid/output_ports/port-uuid/input_ports/approve",
  "status_code": 200,
  "request": "{\"consuming_data_product_id\":\"consumer-uuid\"}",
  "response": "{...}"
}
```

**Result:**
- Consumer can read from provider's S3 paths:
  - `s3://data-products/{provider-namespace}/staging/*.parquet`
  - `s3://data-products/{provider-namespace}/data_mart/*.parquet`
- Documentation file updated in consumer project

**Note on Access Control:**
In this demo, all data products share `minioadmin` credentials. "Access" is granted by documenting which providers a consumer can read from.

In production, you should:
- Create separate MinIO service accounts per data product
- Use MinIO policies to enforce prefix-based access control
- Regenerate consumer credentials when access is granted

---

### 3. Delete Data Product
**Route:** `DELETE /api/data_products/{uuid}`
**Handler:** `handle_delete_data_product(product_id, payload)`

**Triggered when:** A data product is deleted in the portal

**Actions:**
- Placeholder implementation (logs the deletion)
- TODO: Clean up S3 prefix, remove project directory

---

## Architecture

```
Portal → Webhook → Provisioner → Actions
                        ↓
                   ┌────┴────┐
                   ↓         ↓
              S3 Storage  Filesystem
              (MinIO)     (/products/)
```

## S3 Layout

```
data-products/
  ├── product-1/
  │   ├── staging/
  │   │   └── *.parquet
  │   └── data_mart/
  │       └── *.parquet
  ├── product-2/
  │   ├── staging/
  │   └── data_mart/
  └── ...
```

## Environment Variables

- `PROV_DPP_API_URL`: Portal API base URL
- `PROV_TEMPLATE_PATH`: Path to cookiecutter template
- `PROV_TEMPLATE_OUTPUT_PATH`: Where to create projects
- `S3_ENDPOINT`: MinIO endpoint
- `S3_ACCESS_KEY`: MinIO admin access key
- `S3_SECRET_KEY`: MinIO admin secret key

## Testing

Test the provisioner with curl:

```bash
# Test create data product
curl -X POST http://localhost:8090 \
  -H "Content-Type: application/json" \
  -d '{
    "method": "POST",
    "url": "/api/data_products",
    "response": "{\"id\":\"test-uuid\",\"namespace\":\"test-product\"}"
  }'

# Test approve access
curl -X POST http://localhost:8090 \
  -H "Content-Type: application/json" \
  -d '{
    "method": "POST",
    "url": "/api/v2/data_products/provider-id/output_ports/port-id/input_ports/approve",
    "status_code": 200,
    "request": "{\"consuming_data_product_id\":\"consumer-id\"}"
  }'
```
