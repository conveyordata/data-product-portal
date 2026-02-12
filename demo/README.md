# Data Product Portal - Local POC Demo

This demo shows a complete local proof-of-concept for the Data Product Portal with:
- **rustfs**: S3-compatible storage
- **Provisioner**: Handles portal webhooks to scaffold data products
- **Coder**: VS Code in browser for development
- **RStudio**: R development environment

## Architecture

```
┌─────────────────┐
│  Portal (8080)  │
└────────┬────────┘
         │ webhooks
         ↓
┌─────────────────┐     ┌──────────────┐
│  Provisioner    │────→│  rustfs S3   │
│     (8090)      │     │   (9000)     │
└────────┬────────┘     └──────────────┘
         │
         │ scaffolds
         ↓
    /products/
         ↑
         │ mounted in
    ┌────┴─────┬──────────┐
    │          │          │
┌───┴───┐  ┌──┴───┐  ┌───┴────┐
│ Coder │  │RStudio│  │ local  │
│ 8443  │  │ 8787  │  │  dev   │
└───────┘  └───────┘  └────────┘
```

## Quick Start

### 1. Start the Portal Backend

From the project root, start PostgreSQL and the backend:

```bash
# Start PostgreSQL
docker compose up postgresql -d

# Run backend (with webhook URL configured)
cd backend
export WEBHOOK_URL=http://localhost:8090
export WEBHOOK_SECRET=demo-secret-key
python -m uvicorn app.main:app --reload --port 8080
```

Or add to your backend `.env`:
```env
WEBHOOK_URL=http://localhost:8090
WEBHOOK_SECRET=demo-secret-key
```

### 2. Start the Demo Stack

```bash
cd demo
docker compose up
```
This starts:
- **rustfs** (S3): http://localhost:9000 (console: http://localhost:9001)
- **Provisioner**: http://localhost:8090
- **Coder** (VS Code): http://localhost:8443 (password: `coder`)
- **RStudio**: http://localhost:8787 (user: `rstudio`, password: `rstudio`)

### 3. Create a Data Product in Portal

1. Open the portal at http://localhost:8080
2. Create a new data product with:
   - Name: `My Data Product`
   - Namespace: `my-data-product`
   - Fill in other required fields

3. The provisioner will:
   - Scaffold a SQLMesh project in `demo/products/my-data-product/`
   - Create S3 bucket and prefix: `data-products/my-data-product`
   - Generate AWS-style credentials
   - Write `.env` file with S3 configuration

### 4. Open in Development Environment

**Option A: VS Code (Coder)**
1. Navigate to http://localhost:8443
2. Password: `coder`
3. Open `workspace/products/my-data-product`

**Option B: RStudio**
1. Navigate to http://localhost:8787
2. Username: `rstudio`, Password: `rstudio`
3. Open `products/my-data-product`

### 5. Verify S3 Access

Check the S3 console at http://localhost:9001:
- Username: `minioadmin`
- Password: `minioadmin`
- You should see bucket `data-products` with prefix `my-data-product/`

## What Gets Created

When you create a data product, the provisioner scaffolds:

```
products/
  my-data-product/
    ├── .env                 # S3 credentials (auto-generated)
    ├── .gitignore
    ├── README.md
    ├── config.yaml          # SQLMesh configuration
    └── models/
        └── example.sql      # Example SQLMesh model
```

### `.env` Contents

```env
S3_ENDPOINT=http://rustfs:9000
S3_BUCKET=data-products
S3_PREFIX=my-data-product
S3_ACCESS_KEY=AKIAxxxxxxxxxxxxxxxx
S3_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Access Approval Flow

When a consumer data product requests access to another data product:

1. Approve the link in the portal
2. The provisioner will:
   - Generate **new credentials** for the consumer
   - Update the consumer's `.env` file
   - Consumer can now access the producer's S3 data

## Development Workflow

1. **Create** data product in portal → Project scaffolded
2. **Open** project in Coder/RStudio
3. **Develop** SQLMesh models:
   ```bash
   cd /workspace/products/my-data-product
   sqlmesh plan
   sqlmesh run
   ```
4. **Approve** access links → Consumer credentials regenerated

## Configuration

### Environment Variables

**Portal Backend:**
```env
WEBHOOK_URL=http://localhost:8090      # Provisioner URL
WEBHOOK_SECRET=demo-secret-key         # Optional webhook signing
```

**Provisioner:**
```env
PROV_DPP_API_URL=http://localhost:8080  # Portal API URL
PROV_TEMPLATE_PATH=/templates/sqlmesh   # Template location
PROV_TEMPLATE_OUTPUT_PATH=/products     # Output directory
S3_ENDPOINT=http://rustfs:9000          # S3 endpoint
S3_ACCESS_KEY=minioadmin                # S3 admin credentials
S3_SECRET_KEY=minioadmin
```

## Accessing Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Portal | http://localhost:8080 | Default login |
| Provisioner | http://localhost:8090 | N/A (webhook only) |
| S3 (MinIO UI) | http://localhost:9001 | minioadmin / minioadmin |
| Coder (VS Code) | http://localhost:8443 | coder |
| RStudio | http://localhost:8787 | rstudio / rstudio |

## Troubleshooting

### Provisioner not receiving webhooks

Check that `WEBHOOK_URL` is set in the portal backend environment:
```bash
echo $WEBHOOK_URL
# Should output: http://localhost:8090
```

View provisioner logs:
```bash
cd demo
docker compose logs -f provisioner
```

### Project not scaffolded

1. Check provisioner logs for errors
2. Verify templates exist in `demo/templates/sqlmesh/`
3. Ensure `demo/products/` directory is writable

### S3 connection issues

1. Verify rustfs is running: `docker compose ps`
2. Check S3 endpoint is accessible: `curl http://localhost:9000`
3. Try MinIO console: http://localhost:9001

### Cannot open project in Coder/RStudio

1. Verify volume mounts in `docker-compose.yml`
2. Check that project exists in `demo/products/`
3. Restart the services: `docker compose restart coder rstudio`

## Architecture Details

### Webhook Flow

1. User creates data product in portal (POST `/api/data_products`)
2. Portal calls provisioner webhook with:
   ```json
   {
     "method": "POST",
     "url": "/api/data_products",
     "response": "{\"id\": \"uuid\"}",
     "status_code": 200
   }
   ```
3. Provisioner:
   - Fetches full data product details
   - Creates S3 prefix
   - Generates credentials
   - Scaffolds SQLMesh project
   - Writes `.env` file

### Credential Generation

Credentials are AWS-compatible:
- **Access Key**: 20 chars, format `AKIA****************`
- **Secret Key**: 40 chars, alphanumeric + special chars

Stored in-memory in provisioner (in production, use a secrets manager).

### SQLMesh Template

Based on Cookiecutter template at `demo/templates/sqlmesh/`:
- Uses DuckDB by default (file-based, simple)
- Can be modified to use other backends
- Includes example model

## Production Considerations

This is a **demo/POC only**. For production:

- [ ] Use real S3 (AWS/GCP/Azure)
- [ ] Implement proper secrets management
- [ ] Add authentication/authorization to provisioner
- [ ] Use persistent storage for credentials
- [ ] Add monitoring and logging
- [ ] Implement proper error handling
- [ ] Add retry logic for webhook failures
- [ ] Use HTTPS for all services
- [ ] Add webhook signature verification
- [ ] Implement proper lifecycle management

## Next Steps

- Customize SQLMesh template for your needs
- Add additional provisioning steps (databases, notebooks, etc.)
- Integrate with CI/CD pipelines
- Add governance policies
- Implement data quality checks

## Resources

- [SQLMesh Documentation](https://sqlmesh.com)
- [rustfs (MinIO) Documentation](https://min.io/docs/minio/linux/operations/install-deploy-manage/deploy-minio-single-node-single-drive.html)
- [Coder Documentation](https://coder.com/docs)
- [Project Repository](https://github.com/datamindedbe/data-product-portal)
