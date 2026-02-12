# Demo Testing Guide

## Acceptance Criteria Checklist

Use this checklist to verify the POC works as expected.

### ✅ Setup Verification

- [ ] PostgreSQL is running: `docker compose -f ../compose.yaml ps postgresql`
- [ ] Backend is running with webhook URL set: `curl http://localhost:8080/`
- [ ] Check backend logs show: `WEBHOOK_URL` is set
- [ ] Demo services are running: `docker compose ps`
  - [ ] rustfs (S3) - port 9000
  - [ ] provisioner - port 8090
  - [ ] coder - port 8443
  - [ ] rstudio - port 8787

### ✅ Data Product Creation

1. **Create a data product in the portal:**
   - [ ] Portal UI loads at http://localhost:8080
   - [ ] Create new data product with namespace: `test-product`
   - [ ] Check provisioner logs: `docker compose logs provisioner`
   - [ ] Verify webhook received: Look for "Creating data product" message

2. **Verify project scaffolding:**
   - [ ] Project folder exists: `ls -la products/test-product/`
   - [ ] Check folder contains:
     - [ ] `.env` file with S3 credentials
     - [ ] `config.yaml` (SQLMesh config)
     - [ ] `models/` directory
     - [ ] `models/example.sql`
     - [ ] `README.md`
     - [ ] `.gitignore`

3. **Verify .env file contents:**
   ```bash
   cat products/test-product/.env
   ```
   - [ ] Contains `S3_ENDPOINT=http://rustfs:9000`
   - [ ] Contains `S3_BUCKET=data-products`
   - [ ] Contains `S3_PREFIX=test-product`
   - [ ] Contains `S3_ACCESS_KEY=AKIA...` (20 chars)
   - [ ] Contains `S3_SECRET_KEY=...` (40 chars)

### ✅ S3 Storage Verification

1. **Check S3 bucket via MinIO console:**
   - [ ] Open http://localhost:9001
   - [ ] Login: `minioadmin` / `minioadmin`
   - [ ] Verify bucket `data-products` exists
   - [ ] Verify prefix `test-product/` exists
   - [ ] Verify marker file `.keep` exists

2. **Check via AWS CLI (optional):**
   ```bash
   AWS_ACCESS_KEY_ID=minioadmin \
   AWS_SECRET_ACCESS_KEY=minioadmin \
   aws --endpoint-url=http://localhost:9000 \
   s3 ls s3://data-products/
   ```
   - [ ] Should show `test-product/` prefix

### ✅ Development Environment Access

1. **Coder (VS Code in browser):**
   - [ ] Open http://localhost:8443
   - [ ] Enter password: `coder`
   - [ ] Navigate to `workspace/products/test-product`
   - [ ] Verify all files are visible
   - [ ] Can open and edit `.env` file

2. **RStudio:**
   - [ ] Open http://localhost:8787
   - [ ] Login: `rstudio` / `rstudio`
   - [ ] Navigate to `products/test-product` in file browser
   - [ ] Verify all files are visible
   - [ ] Can view file contents

### ✅ Link Approval (Consumer Credentials)

**Note:** This test requires two data products

1. **Create second data product:**
   - [ ] Create data product with namespace: `consumer-product`
   - [ ] Verify folder created: `products/consumer-product/`
   - [ ] Note the initial credentials in `.env`

2. **Create and approve link:**
   - [ ] In portal, create link from `consumer-product` to `test-product`
   - [ ] Approve the link
   - [ ] Check provisioner logs for "Approving link" message

3. **Verify credential regeneration:**
   - [ ] Check `products/consumer-product/.env`
   - [ ] Credentials should be different from initial ones
   - [ ] New access key starts with `AKIA`
   - [ ] New secret key is 40 characters

### ✅ End-to-End Workflow

Complete workflow test:

1. [ ] Create data product in portal
2. [ ] Provisioner receives webhook
3. [ ] Project scaffolded in `products/`
4. [ ] S3 prefix created
5. [ ] `.env` file written with credentials
6. [ ] Can open project in Coder
7. [ ] Can open project in RStudio
8. [ ] Create second data product
9. [ ] Request link between products
10. [ ] Approve link
11. [ ] Consumer credentials regenerated

## Common Issues

### Project not created
```bash
# Check provisioner logs
docker compose logs provisioner

# Check if webhook URL is set in backend
curl http://localhost:8080/  # Backend should be running

# Verify templates exist
ls -la templates/sqlmesh/
```

### S3 connection failed
```bash
# Check if rustfs is running
docker compose ps rustfs

# Try accessing S3 directly
curl http://localhost:9000

# Check provisioner can reach rustfs
docker compose exec provisioner curl http://rustfs:9000
```

### Files not visible in Coder/RStudio
```bash
# Check volume mounts
docker compose config | grep -A 5 "volumes:"

# Restart services
docker compose restart coder rstudio

# Check permissions
ls -la products/
```

## Success Criteria

The POC is successful when:

✅ **Creation Flow:**
- Portal → Provisioner webhook → SQLMesh project scaffolded
- S3 bucket and prefix created
- Credentials generated and written to `.env`

✅ **Access Flow:**
- Can open project in Coder (VS Code)
- Can open project in RStudio
- Both environments see the same files

✅ **Link Approval:**
- Approving link regenerates consumer credentials
- Consumer `.env` updated with new credentials
- Producer project unchanged

## Manual Testing Script

Run this to test the full flow:

```bash
# 1. Setup
cd demo
./start.sh

# 2. Create test product via portal API (or use UI)
curl -X POST http://localhost:8080/api/data_products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "namespace": "test-product",
    "description": "Testing the POC",
    "type_id": "<type-id>",
    "lifecycle_id": "<lifecycle-id>",
    "domain_id": "<domain-id>",
    "tag_ids": [],
    "owners": ["<user-id>"]
  }'

# 3. Verify scaffolding
ls -la products/test-product/
cat products/test-product/.env

# 4. Check S3
AWS_ACCESS_KEY_ID=minioadmin \
AWS_SECRET_ACCESS_KEY=minioadmin \
aws --endpoint-url=http://localhost:9000 s3 ls s3://data-products/

# 5. Open in browser
open http://localhost:8443  # Coder
open http://localhost:8787  # RStudio
open http://localhost:9001  # S3 Console

echo "✅ All tests passed!"
```

## Cleanup

After testing:

```bash
# Stop all services
docker compose down

# Remove generated projects (optional)
rm -rf products/*

# Remove S3 data (optional)
rm -rf s3/*
```
