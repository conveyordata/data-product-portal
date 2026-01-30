# Quick Start: Plugin System

## Installation & Testing

### 1. Test Internal Plugins (Already Working)

```bash
cd backend
poetry run python ../plugins/test_plugins.py
```

Expected output shows 4-5 plugins discovered.

### 2. Install S3 External Plugin

```bash
cd plugins/s3_plugin
/path/to/backend/.venv/bin/pip install -e .
# Or if using poetry in backend:
cd ../../backend
poetry run pip install -e ../plugins/s3_plugin
```

### 3. Verify External Plugin

```bash
cd backend
poetry run python ../plugins/test_plugins.py
```

You should now see S3DataOutput listed with source `s3_plugin.schema`.

### 4. Start the Backend

```bash
cd backend
poetry run python -m app.local_startup
```

Check logs for:
```
INFO: Initialized 5 plugins
```

### 5. Test API Endpoints

```bash
# List all plugins
curl http://localhost:8080/api/v2/plugins/

# Get S3 plugin form
curl http://localhost:8080/api/v2/plugins/S3DataOutput/form
```

## Configuration Options

### Use Default Plugins (No Configuration)

Default: Snowflake, Databricks, Glue, Redshift + any external plugins

### Use Specific Plugins Only

In `.env`:
```bash
ENABLED_PLUGINS=app.data_output_configuration.snowflake.schema.SnowflakeDataOutput,app.data_output_configuration.glue.schema.GlueDataOutput
```

### Disable All Internal Plugins

```bash
# Only external plugins will be loaded
ENABLED_PLUGINS=
```

## Creating Your Own Plugin

### 1. Create Package Structure

```bash
mkdir -p my-plugin/my_plugin
cd my-plugin
```

### 2. Create pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-data-output-plugin"
version = "1.0.0"
dependencies = ["pydantic>=2.0.0", "sqlalchemy>=2.0.0"]

[project.entry-points."data_product_portal.plugins"]
MyPlugin = "my_plugin.schema:MyDataOutput"
```

### 3. Create schema.py

```python
from typing import ClassVar, Literal
from app.data_output_configuration.base_schema import (
    AssetProviderPlugin, PlatformMetadata, UIElementMetadata
)
from app.data_output_configuration.data_output_types import DataOutputTypes

class MyDataOutput(AssetProviderPlugin):
    name: ClassVar[str] = "MyDataOutput"
    version: ClassVar[str] = "1.0"
    migration_file_path: ClassVar[str] = "path/to/migration.py"

    configuration_type: Literal[DataOutputTypes.MyDataOutput]
    my_field: str

    _platform_metadata = PlatformMetadata(
        display_name="My Platform",
        icon_name="my-logo.svg",
        platform_key="my_platform",
    )

    @classmethod
    def get_ui_metadata(cls, db) -> list[UIElementMetadata]:
        return []  # Add form fields
```

### 4. Install & Test

```bash
pip install -e .
poetry run python ../plugins/test_plugins.py
```

## Troubleshooting

### Plugin Not Found

```bash
# Check entry points
python -c "from importlib.metadata import entry_points; print(list(entry_points().select(group='data_product_portal.plugins')))"

# Verify installation
pip show my-data-output-plugin
```

### Import Errors

Make sure plugin is installed in same environment as backend:
```bash
cd backend
poetry run pip install -e ../path/to/my-plugin
```

### Schema Validation Warnings

The warnings about "schema" field shadowing are harmless - they indicate Pydantic fields named "schema" shadow a method in the base class. This is expected for database schema fields.

## Migration Discovery

```python
from app.data_output_configuration.registry import PluginRegistry

# Initialize registry
PluginRegistry.discover_and_register()

# Get all migrations
migrations = PluginRegistry.get_all_migrations()
for plugin_name, migration_path in migrations.items():
    print(f"{plugin_name}: {migration_path}")
```

## Next Steps

1. Read [plugin-system.md](../docs/docs/developer-guide/plugin-system.md) for detailed guide
2. Check [PLUGIN_IMPLEMENTATION_SUMMARY.md](../PLUGIN_IMPLEMENTATION_SUMMARY.md) for architecture
3. Review S3 plugin example in `plugins/s3_plugin/`
4. Create your own plugin following the template
