"""
Test script to verify plugin system functionality
"""

import sys
from pathlib import Path

# Add backend to path before any app imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.data_output_configuration.registry import PluginRegistry  # noqa: E402


def test_plugin_registry():
    """Test plugin registry discovery"""
    print("=== Testing Plugin Registry ===\n")

    # Reset registry for clean test
    PluginRegistry.reset()

    # Test 1: Discover default internal plugins
    print("1. Discovering internal plugins...")
    PluginRegistry.discover_and_register()

    plugins = PluginRegistry.get_all()
    print(f"   Found {len(plugins)} plugins:")
    for plugin in plugins:
        print(f"   - {plugin.__name__} (v{plugin.version})")
        if plugin.migration_file_path:
            print(f"     Migration: {plugin.migration_file_path}")

    # Test 2: Check migration paths
    print("\n2. Checking migration paths...")
    migrations = PluginRegistry.get_all_migrations()
    print(f"   Found {len(migrations)} migrations:")
    for name, path in migrations.items():
        print(f"   - {name}: {path}")

    # Test 3: Get specific plugin
    print("\n3. Testing specific plugin retrieval...")
    snowflake = PluginRegistry.get("SnowflakeDataOutput")
    if snowflake:
        print("   ✓ Successfully retrieved SnowflakeDataOutput")
        print(f"     Version: {snowflake.version}")
        print(f"     Migration: {snowflake.migration_file_path}")
    else:
        print("   ✗ Failed to retrieve SnowflakeDataOutput")

    print("\n=== Plugin Registry Test Complete ===")
    return len(plugins) > 0


def test_external_plugin():
    """Test external plugin installation"""
    print("\n=== Testing External Plugin ===\n")

    # Reset registry
    PluginRegistry.reset()

    print("1. Discovering plugins with entry points...")
    PluginRegistry.discover_and_register()

    s3_plugin = PluginRegistry.get("S3DataOutput")
    if s3_plugin:
        print("   ✓ S3DataOutput plugin found!")
        print(f"     Source: {s3_plugin.__module__}")
        print(f"     Version: {s3_plugin.version}")
        print(f"     Migration: {s3_plugin.migration_file_path}")
        return True
    else:
        print("   ℹ S3DataOutput not found (external plugin not installed)")
        print("     To install: cd plugins/s3_plugin && pip install -e .")
        return False


if __name__ == "__main__":
    success = test_plugin_registry()

    # Test external plugin (may not be installed)
    external_success = test_external_plugin()

    if success:
        print("\n✓ Plugin system is working correctly!")
        if external_success:
            print("✓ External plugin system verified!")
        sys.exit(0)
    else:
        print("\n✗ Plugin system test failed!")
        sys.exit(1)
