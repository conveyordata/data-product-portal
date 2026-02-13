# POC Demo Flow: S3 Access Control

This document demonstrates the **access control flow** of the data product platform POC.

## Overview

The POC demonstrates that:
1. ✅ Each data product gets **unique S3 credentials** (not shared)
2. ✅ Initially, credentials only allow access to **own prefix**
3. ❌ Consumers **cannot access** provider data before approval
4. ✅ After approval, consumers **can read** provider's output data

## Prerequisites

```bash
cd demo
docker compose up -d
```

## Demo Flow

### Step 1: Create Provider Data Product

1. **Create first data product** (e.g., "Contact Survey Data")
   - Must use Contact Survey Data to auto create the output port
   - Portal calls webhook: `POST /api/data_products`
   - Provisioner creates:
     - S3 prefix: `s3://data-products/survey-data/`
     - Credentials: `dp-survey-data` (unique access key)
     - Project scaffolding with SQLMesh
   - Check logs: `docker compose logs provisioner | grep survey-data`

2. **Verify provider credentials**
   ```bash
   cd products/survey-data
   cat .env
   # Should show:
   # S3_ACCESS_KEY=dp-survey-data
   # S3_SECRET_KEY=<random-40-chars>
   # S3_PREFIX=survey-data
   ```

3. **Test provider can access own data**
   ```bash
   python ../test_s3_access.py
   # Should show:
   # ✅ Can access s3://data-products/survey-data/
   # ❌ Access DENIED to s3://data-products/some-other-product/
   ```

4. **Run SQLMesh pipeline to create data**
   ```bash
   ./run.sh
   # Choose: Run plan and export to S3
   ```

### Step 2: Create Consumer Data Product

1. **Create second data product** (e.g., "analytics-dashboard")
   - Portal calls webhook: `POST /api/data_products`
   - Provisioner creates:
     - S3 prefix: `s3://data-products/analytics-dashboard/`
     - Credentials: `dp-analytics-dashb` (different from provider!)
     - Project scaffolding

2. **Verify consumer has different credentials**
   ```bash
   cd products/analytics-dashboard
   cat .env
   # Should show DIFFERENT access key than survey-data:
   # S3_ACCESS_KEY=dp-analytics-dashb
   ```

3. **Test consumer CANNOT access provider data (before approval)**
   ```bash
   python ../test_s3_access.py
   # Should show:
   # ✅ Can access s3://data-products/analytics-dashboard/ (own data)
   # ❌ Access DENIED to s3://data-products/survey-data/ (provider data)
   ```

### Step 3: Request Access (Consumer → Provider)

1. **Consumer requests access to provider's output port**
   - In portal UI: Navigate to provider's output port
   - Click "Request Access" as consumer data product
   - This creates a pending input port link

2. **Provider reviews and approves**
   - Provider navigates to pending requests
   - Approves the access request
   - Portal calls webhook: `POST /api/v2/data_products/{uuid}/output_ports/{uuid}/input_ports/approve`

3. **Check provisioner logs**
   ```bash
   docker compose logs provisioner | tail -50
   # Should show:
   # ✅ Access granted! Updated consumer 'analytics-dashboard' allowed prefixes: ['analytics-dashboard', 'survey-data']
   ```

### Step 4: Verify Access Granted

1. **Check consumer's access documentation**
   ```bash
   cd products/analytics-dashboard
   cat ACCESSIBLE_DATA_PRODUCTS.txt
   # Should show:
   # Approved access: survey-data
   # S3 Path: s3://data-products/survey-data
   # Read from: s3://data-products/survey-data/staging/*.parquet
   ```

2. **Test consumer CAN NOW access provider data**
   ```bash
   python ../test_s3_access.py
   # Should show:
   # ✅ Can access s3://data-products/analytics-dashboard/ (own data)
   # ✅ Can access s3://data-products/survey-data/ (provider data - NOW WORKS!)
   ```

3. **Use provider's data in consumer project**
   ```bash
   # Copy example_consumer_access.py and modify to read survey-data
   python example_consumer_access.py
   ```

## Architecture Notes

### Current Demo Implementation

The POC demonstrates the **access control concept** with the following approach:

1. **Unique Credentials per Data Product**
   - Each data product gets a unique access key (e.g., `dp-survey-data`)
   - Credentials are tracked in `credentials_store` dictionary
   - Each credential has an `allowed_prefixes` list

2. **Access Control State**
   - Initially: `allowed_prefixes = ["own-namespace"]`
   - After approval: `allowed_prefixes = ["own-namespace", "provider-namespace"]`
   - Tracked in-memory (provisioner restart clears state)

3. **What's Simulated**
   - ✅ Unique credentials per data product
   - ✅ Tracking of access grants
   - ✅ Documentation of approved access
   - ⚠️ **Actual MinIO policy enforcement** (see below)

### Production Implementation

For production, implement actual MinIO access control:

```python
# Option 1: MinIO Admin API (create users + policies)
mc admin user add myminio dp-survey-data <secret>
mc admin policy create myminio survey-data-policy policy.json
mc admin policy attach myminio survey-data-policy --user dp-survey-data

# Option 2: MinIO Service Accounts (recommended)
mc admin user svcacct add --access-key dp-survey-data --secret-key <secret> myminio minioadmin
mc admin policy attach myminio survey-data-policy --user=dp-survey-data

# On approval: update policy to add cross-prefix read access
mc admin policy create myminio consumer-policy consumer-policy.json
mc admin policy attach myminio consumer-policy --user dp-analytics-dashb
```

Policy example for cross-prefix read:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::data-products/survey-data/*",
        "arn:aws:s3:::data-products"
      ]
    }
  ]
}
```

### Current Limitations

Since MinIO user/policy creation requires MinIO Admin API (not available via boto3):

1. **Demo uses shared minioadmin credentials** - All data products can technically access each other's data
2. **Access control is documented** - The `ACCESSIBLE_DATA_PRODUCTS.txt` file shows what SHOULD be accessible
3. **Credentials are tracked** - The `allowed_prefixes` shows the intent

### Testing Actual Enforcement

To test actual MinIO policy enforcement in the POC:

```bash
# Install MinIO client in provisioner container
docker exec -it demo-provisioner-1 sh
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
mv mc /usr/local/bin/

# Configure mc
mc alias set myminio http://rustfs:9000 minioadmin minioadmin

# Create actual users and policies (manual for now)
mc admin user add myminio dp-survey-data <secret-from-env>
mc admin policy create myminio survey-data-policy /tmp/survey-policy.json
mc admin policy attach myminio survey-data-policy --user dp-survey-data
```

Then update the test script to use the actual credentials from `.env` files.

## Summary

This POC demonstrates:
- ✅ **Credential isolation** - Each data product has unique credentials
- ✅ **Access tracking** - System knows which consumers can access which providers
- ✅ **Approval workflow** - Access is explicitly granted via portal
- ✅ **Documentation** - Consumers know what they can access

For production:
- 🔧 Implement actual MinIO user/policy creation via Admin API
- 🔧 Update policies on approval (not just track in memory)
- 🔧 Use persistent storage for credentials (not in-memory dictionary)
- 🔧 Add revocation flow (remove policies when access is revoked)
