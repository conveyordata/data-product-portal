#!/usr/bin/env python3
"""
Example: How a consumer data product reads from {{ cookiecutter.project_name }}

Consumers read from PARQUET FILES on S3 after the producer runs export_to_s3.py.

Prerequisites:
- Consumer has been approved for access via the portal
- Consumer has regenerated S3 credentials in their .env
- Producer has run export_to_s3.py to publish data
"""

import duckdb
import os
from pathlib import Path

# Simple .env loader
env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ[key] = value


def consumer_reads_data():
    """
    Example of how a consumer reads from this data product
    """

    print("=" * 70)
    print("CONSUMER: Reading from {{ cookiecutter.project_name }}")
    print("=" * 70)
    print()

    endpoint_host = os.getenv("S3_ENDPOINT_HOST", "localhost")
    access_key = os.getenv("S3_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("S3_SECRET_KEY", "minioadmin")
    bucket = os.getenv("S3_BUCKET", "data-products")
    producer_prefix = "{{ cookiecutter.project_name }}"

    print("📦 Reading Parquet files from S3...")
    print(f"   Endpoint: {endpoint_host}:9000")
    print(f"   Location: s3://{bucket}/{producer_prefix}/")
    print()

    try:
        conn = duckdb.connect()
        conn.execute("INSTALL httpfs; LOAD httpfs;")

        # Configure S3
        conn.execute(f"""
            CREATE SECRET s3_secret (
                TYPE S3,
                ENDPOINT '{endpoint_host}:9000',
                KEY_ID '{access_key}',
                SECRET '{secret_key}',
                USE_SSL false,
                URL_STYLE 'path',
                REGION 'us-east-1'
            );
        """)

        # List available tables (parquet files)
        print("📊 Available tables:")

        # Try to list files in data_mart
        try:
            # This is an example - adjust based on your actual models
            files = conn.execute(f"""
                SELECT * FROM glob('s3://{bucket}/{producer_prefix}/data_mart/*.parquet')
            """).fetchall()

            print(f"   Found {len(files)} table(s) in data_mart/")
            for f in files:
                print(f"   - {f[0].split('/')[-1]}")
        except Exception as e:
            print(f"   No tables found yet: {e}")

        print()
        print("💡 Example query:")
        print(
            f"   SELECT * FROM 's3://{bucket}/{producer_prefix}/data_mart/your_table.parquet'"
        )

        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Tip: Producer needs to run 'python export_to_s3.py' first")


if __name__ == "__main__":
    print()
    print("🔄 CONSUMER ACCESS EXAMPLE")
    print()
    print("This demonstrates how consumers read from {{ cookiecutter.project_name }}:")
    print("  1. Producer runs SQLMesh pipeline")
    print("  2. Producer runs export_to_s3.py")
    print("  3. Consumer reads Parquet files from S3")
    print()
    input("Press Enter to run the example...")

    consumer_reads_data()
