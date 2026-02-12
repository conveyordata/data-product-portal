#!/usr/bin/env python3
"""
Test script to verify S3 access control.
Run this from within your data product directory.

This script tests:
1. Access to your own S3 prefix (should work)
2. Access to approved provider prefixes (should work after approval)
3. Access to unapproved prefixes (should fail)
"""

import sys
from pathlib import Path
import boto3
from botocore.exceptions import ClientError


def load_env():
    """Load environment variables from .env file"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ No .env file found. Run this from a data product directory.")
        sys.exit(1)

    env_vars = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key] = value

    return env_vars


def test_s3_access(env_vars, prefix, description=""):
    """Test if we can list objects in a specific S3 prefix"""
    s3_client = boto3.client(
        "s3",
        endpoint_url=env_vars.get("S3_ENDPOINT", "http://localhost:9000"),
        aws_access_key_id=env_vars["S3_ACCESS_KEY"],
        aws_secret_access_key=env_vars["S3_SECRET_KEY"],
    )

    bucket = env_vars["S3_BUCKET"]

    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket, Prefix=f"{prefix}/", MaxKeys=10
        )

        if "Contents" in response:
            count = len(response["Contents"])
            print(f"  ✅ CAN ACCESS s3://{bucket}/{prefix}/")
            if description:
                print(f"     {description}")
            print(f"     Found {count} objects:")
            for obj in response.get("Contents", [])[:5]:
                print(f"       - {obj['Key']}")
            if count > 5:
                print(f"       ... and {count - 5} more")
            return True
        else:
            print(f"  ✅ CAN ACCESS s3://{bucket}/{prefix}/ (empty)")
            if description:
                print(f"     {description}")
            return True

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "AccessDenied":
            print(f"  ❌ ACCESS DENIED to s3://{bucket}/{prefix}/")
            if description:
                print(f"     {description}")
            return False
        else:
            print(f"  ⚠️  Error: {error_code}")
            return False


def main():
    print("\n" + "=" * 70)
    print("🔒 S3 ACCESS CONTROL TEST")
    print("=" * 70)

    env_vars = load_env()

    print("\n📋 Your Credentials:")
    print(f"   Access Key: {env_vars['S3_ACCESS_KEY']}")
    print(f"   Secret Key: {env_vars['S3_SECRET_KEY'][:10]}...")
    print(f"   Bucket:     {env_vars['S3_BUCKET']}")
    print(f"   Your Data:  {env_vars['S3_PREFIX']}")

    # Test 1: Access to own prefix
    print("\n🔓 Test 1: YOUR OWN DATA (should work)")
    print(f"   Testing: s3://{env_vars['S3_BUCKET']}/{env_vars['S3_PREFIX']}")
    own_access = test_s3_access(
        env_vars, env_vars["S3_PREFIX"], "You always have access to your own data"
    )

    # Test 2: Access to approved providers
    accessible_file = Path("ACCESSIBLE_DATA_PRODUCTS.txt")
    if accessible_file.exists():
        print("\n✅ Test 2: APPROVED PROVIDERS (should work after approval)")

        with open(accessible_file) as f:
            content = f.read()

        # Extract provider namespaces and paths
        import re

        matches = re.findall(r"# Approved access: (\S+)\n# S3 Path: (\S+)", content)

        if matches:
            for namespace, s3_path in matches:
                prefix = s3_path.replace(f"s3://{env_vars['S3_BUCKET']}/", "")
                test_s3_access(env_vars, prefix, "Approved access granted via portal")
        else:
            print("  📝 No approved providers found in ACCESSIBLE_DATA_PRODUCTS.txt")
    else:
        print("\n📝 Test 2: APPROVED PROVIDERS")
        print("   No ACCESSIBLE_DATA_PRODUCTS.txt file yet")
        print(
            "   This file is created when you get approved access to other data products"
        )

    # Test 3: Try accessing a random prefix (should fail)
    print("\n🚫 Test 3: UNAPPROVED DATA PRODUCT (should fail)")
    print(f"   Testing: s3://{env_vars['S3_BUCKET']}/some-other-product")
    test_s3_access(
        env_vars,
        "some-other-product",
        "This should be denied - you haven't requested access",
    )

    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"✅ Your own data: {'ACCESSIBLE' if own_access else 'ERROR'}")

    if accessible_file.exists():
        import re

        content = accessible_file.read_text()
        approved_count = len(re.findall(r"# Approved access:", content))
        print(f"✅ Approved providers: {approved_count}")
    else:
        print("📝 Approved providers: None yet")

    print("\n💡 To request access to another data product:")
    print("   1. Navigate to their output port in the portal")
    print("   2. Click 'Request Access' as this data product")
    print("   3. Wait for provider approval")
    print("   4. Run this script again to verify access\n")


if __name__ == "__main__":
    main()
