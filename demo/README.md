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
- **Documentation**: http://localhost:8888/docs (auto-rendered Quarto docs)
- **Coder** (VS Code): http://localhost:8443 (password: `coder`)
- **RStudio**: http://localhost:8787 (user: `rstudio`, password: `rstudio`)

### 3. Demo Data Product (Auto-Created)

When the provisioner starts, it automatically creates the **CoMix Survey Data** demo product with:
- Comprehensive COVID-19 social contact survey data
- Extensive about/documentation section
- Auto-scaffolded SQLMesh project
- S3 credentials and configuration
- Quarto documentation

Check the provisioner logs to see the bootstrap:
```bash
docker compose logs -f provisioner
```

**Creating Additional Data Products**

To create more data products manually:

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
   - Create `docs/` directory with Quarto documentation
   - Render documentation to http://localhost:8888/docs/my-data-product

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
    ├── models/              # SQLMesh models
    │   ├── example_staging.py
    │   └── example_data_mart.py
    ├── docs/                # Quarto documentation
    │   ├── _quarto.yml      # Quarto config
    │   ├── index.qmd        # Homepage
    │   ├── data-dictionary.qmd
    │   ├── usage-guide.qmd
    │   └── styles.css
    ├── export_to_s3.py      # Export script
    ├── run.sh               # Pipeline runner
    └── test_s3_access.py    # S3 access tester
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

## Importing Existing SQLMesh Projects

If you have an existing SQLMesh project to import:

```bash
./import_project.sh <source-directory> <data-product-name>
```

**Example:**
```bash
# 1. Create data product in portal first (to reserve namespace and get credentials)
# 2. Import your existing project
./import_project.sh ~/projects/my-sqlmesh-pipeline my-data-product

# 3. The script will:
#    - Copy project files to demo/products/my-data-product/
#    - Preserve S3 credentials from scaffolded .env
#    - Skip .git, __pycache__, venv, etc.
```

**Tips:**
- Create the data product in the portal FIRST to get S3 credentials
- Review and update `config.yaml` with S3 settings after import
- Check `.env` file has the correct S3 credentials

## Cleaning/Resetting the Demo

To completely reset the demo to a clean state:

```bash
./clean.sh
```

This will:
- ✅ Stop all services (docker compose down)
- ✅ Remove all scaffolded data products from `products/`
- ✅ Clear all S3 data
- ✅ Remove Docker volumes
- ⚙️  Optionally clear Docker build cache

**⚠️  Warning**: This deletes ALL demo data. Your portal database (PostgreSQL) is not affected.

After cleaning, restart with:
```bash
./start.sh
```

Or to start fresh with a new backend database too:
```bash
cd ..
docker compose down -v  # Removes PostgreSQL data
docker compose up postgresql -d
# Then run backend and demo/start.sh
```

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
| Portal | http://localhost:5050 | Default login |
| Provisioner | http://localhost:8090 | N/A (webhook only) |
| Documentation | http://localhost:8888/docs | N/A (public) |
| S3 (MinIO UI) | http://localhost:9001 | minioadmin / minioadmin |
| Coder (VS Code) | http://localhost:8443 | coder |
| RStudio | http://localhost:8787 | rstudio / rstudio |

## Documentation

Each data product automatically gets Quarto documentation that is rendered and served at:
- **All docs index**: http://localhost:8888/docs
- **Specific data product**: http://localhost:8888/docs/{data-product-name}

### What's Included

Every scaffolded data product includes a `docs/` directory with:
- **index.qmd** - Homepage with overview and quick start
- **data-dictionary.qmd** - Schema and table documentation
- **usage-guide.qmd** - Guide for consumers and providers
- **_quarto.yml** - Quarto configuration
- **styles.css** - Custom styling

### How It Works

1. **Auto-rendering**: The `quarto` container watches `/products` for changes
2. **Detection**: When a data product is created with a `docs/` directory, it's detected
3. **Rendering**: Quarto renders the docs to HTML
4. **Serving**: Nginx serves the rendered docs at port 8888

### Customizing Documentation

Edit the `.qmd` files in your data product's `docs/` directory:

```bash
cd products/my-data-product/docs
# Edit index.qmd, data-dictionary.qmd, etc.
```

The docs will automatically re-render when you save changes. Refresh your browser to see updates.

### Adding Pages

1. Create a new `.qmd` file in `docs/`
2. Add it to the navbar in `_quarto.yml`:
   ```yaml
   navbar:
     left:
       - text: "My New Page"
         href: my-new-page.qmd
   ```
3. The page will be automatically rendered

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
