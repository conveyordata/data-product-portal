# Data Product Portal Plugins

This directory contains external plugins for the Data Product Portal and plugin development tools.

## Contents

- **s3_plugin/** - Example external S3 data output plugin (pip installable)
- **test_plugins.py** - Plugin discovery and validation test script
- **test_integration.py** - Full integration test for plugin system
- **QUICKSTART.md** - Quick start guide for using and creating plugins

## Plugin System Architecture

The Data Product Portal uses a plugin architecture for data output configurations. Plugins can be:

1. **Internal** - Part of the main backend codebase (Snowflake, Databricks, Glue, Redshift)
2. **External** - Separate pip-installable packages discovered via entry points

## Quick Test

```bash
# Test plugin discovery
cd backend
poetry run python ../plugins/test_plugins.py

# Run full integration test
poetry run python ../plugins/test_integration.py
```

## Installing the S3 Example Plugin

The S3 plugin demonstrates how external plugins work:

```bash
cd s3_plugin
pip install -e .
# Or using backend poetry environment:
cd ../backend
poetry run pip install -e ../plugins/s3_plugin
```

Verify installation:
```bash
poetry run python ../plugins/test_plugins.py
```

You should see S3DataOutput listed with source `s3_plugin.schema`.

## Creating Your Own Plugin

See [QUICKSTART.md](QUICKSTART.md) for a step-by-step guide.

For detailed documentation, see [docs/developer-guide/plugin-system.md](../docs/docs/developer-guide/plugin-system.md).

### Basic Plugin Structure

```
my-plugin/
├── setup.py or pyproject.toml    # Package configuration with entry point
├── README.md                       # Plugin documentation
└── my_plugin/
    ├── __init__.py                # Package initialization
    ├── schema.py                  # Pydantic schema (UI + validation)
    └── model.py                   # SQLAlchemy model (database)
```

### Entry Point Registration

**pyproject.toml:**
```toml
[project.entry-points."data_product_portal.plugins"]
MyPlugin = "my_plugin.schema:MyDataOutput"
```

**setup.py:**
```python
setup(
    entry_points={
        "data_product_portal.plugins": [
            "MyPlugin = my_plugin.schema:MyDataOutput",
        ],
    },
)
```

## Plugin Features

Each plugin provides:

- **Schema definition** - Pydantic models for validation
- **UI metadata** - Form fields for frontend configuration
- **Database model** - SQLAlchemy model with dedicated table
- **Migration tracking** - Path to Alembic migration file
- **Platform metadata** - Display name, icon, labels
- **Custom logic** - Validation, template rendering, configuration retrieval

## Testing Your Plugin

1. Install your plugin: `pip install -e /path/to/your-plugin`
2. Run test script: `poetry run python ../plugins/test_plugins.py`
3. Check it appears in the plugin list
4. Verify migration path is correct
5. Start backend and check `/api/v2/plugins/` endpoint

## Available Plugins

### Internal (Default)
- **SnowflakeDataOutput** - Snowflake database configuration
- **DatabricksDataOutput** - Databricks catalog configuration
- **GlueDataOutput** - AWS Glue database configuration
- **RedshiftDataOutput** - AWS Redshift database configuration

### External (Example)
- **S3DataOutput** - AWS S3 bucket configuration (in `s3_plugin/`)

## Configuration

Control which plugins are loaded via environment variable:

```bash
# Use defaults (all internal plugins + discovered external)
ENABLED_PLUGINS=

# Use specific internal plugins only
ENABLED_PLUGINS=app.data_output_configuration.snowflake.schema.SnowflakeDataOutput,app.data_output_configuration.glue.schema.GlueDataOutput

# Use only external plugins (disable all internal)
ENABLED_PLUGINS=
```

External plugins installed via pip are always discovered automatically through entry points.

## Migration Management

Each plugin declares its migration file:

```python
class MyDataOutput(AssetProviderPlugin):
    migration_file_path: ClassVar[str] = "app/database/alembic/versions/2026_01_28_1234-my_table.py"
```

Get all plugin migrations:
```python
from app.data_output_configuration.registry import PluginRegistry
PluginRegistry.discover_and_register()
migrations = PluginRegistry.get_all_migrations()
```

## Troubleshooting

### Plugin not discovered

1. Verify entry point registration: `pip show -f your-plugin | grep entry_points`
2. Check installation: `pip list | grep your-plugin`
3. Look for errors in logs: Check startup logs for "Plugin registry" messages

### Import errors

Ensure plugin is installed in same environment as backend:
```bash
cd backend
poetry run pip install -e ../path/to/your-plugin
```

### Migration not found

Verify the migration file path in your plugin matches the actual file location.

## Documentation

- [Plugin System Guide](../docs/docs/developer-guide/plugin-system.md) - Comprehensive developer guide
- [Implementation Summary](../PLUGIN_IMPLEMENTATION_SUMMARY.md) - Technical implementation details
- [Quick Start](QUICKSTART.md) - Getting started guide
- [ADR-0009](../docs/adr/0009-plugin-data-output-configs.md) - Architecture decision record

## Support

For questions or issues with the plugin system, please refer to the documentation or create an issue in the repository.
