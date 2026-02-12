#!/usr/bin/env python3
"""
Export SQLMesh tables to S3 as Parquet files
This runs after sqlmesh plan/run to push data to S3 for consumers
"""

import duckdb
import os
from pathlib import Path

# Load .env
env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ[key] = value

# Connect to SQLMesh database
conn = duckdb.connect("cnt_survey.duckdb")
conn.execute("LOAD httpfs;")

# Configure S3
endpoint_host = os.getenv("S3_ENDPOINT_HOST", "localhost")
access_key = os.getenv("S3_ACCESS_KEY", "minioadmin")
secret_key = os.getenv("S3_SECRET_KEY", "minioadmin")
bucket = os.getenv("S3_BUCKET", "data-products")
prefix = os.getenv("S3_PREFIX", "{{ cookiecutter.project_name }}")

print(f"Configuring S3: {endpoint_host}:9000")
conn.execute(f"""
    CREATE OR REPLACE SECRET s3_secret (
        TYPE S3,
        ENDPOINT '{endpoint_host}:9000',
        KEY_ID '{access_key}',
        SECRET '{secret_key}',
        USE_SSL false,
        URL_STYLE 'path',
        REGION 'us-east-1'
    );
""")

# Schema to S3 prefix mapping
schema_mapping = {
    "staging": f"s3://{bucket}/{prefix}/staging",
    "data_mart": f"s3://{bucket}/{prefix}/data_mart",
}

print("\n📦 Exporting tables to S3...")

for schema, s3_prefix in schema_mapping.items():
    # Get all tables/views in this schema
    # SQLMesh creates VIEWS in physical schemas that point to versioned tables
    tables_query = f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = '{schema}'
        AND table_type IN ('BASE TABLE', 'VIEW')
    """

    tables = conn.execute(tables_query).fetchall()

    if not tables:
        print(f"\n  {schema}/: No tables or views found")
        continue

    print(f"\n  {schema}/:")

    for (table_name,) in tables:
        # Export table to S3 as Parquet
        s3_path = f"{s3_prefix}/{table_name}.parquet"

        try:
            # Use COPY to export as Parquet
            # This works for both tables and views
            export_query = f"""
                COPY {schema}.{table_name}
                TO '{s3_path}'
                (FORMAT PARQUET, OVERWRITE_OR_IGNORE true)
            """
            conn.execute(export_query)

            # Get row count
            count = conn.execute(
                f"SELECT COUNT(*) FROM {schema}.{table_name}"
            ).fetchone()[0]
            print(f"    ✓ {table_name}.parquet ({count:,} rows)")

        except Exception as e:
            print(f"    ✗ {table_name}: {e}")

conn.close()
print("\n✅ Export complete! Data is now available on S3 for consumers.")
print(
    f"\nConsumers can read from: s3://{bucket}/{prefix}/[staging|data_mart]/*.parquet"
)
