# Plugin System Implementation Guide

This document describes the plugin system for data output configurations in the Data Product Portal.

## Overview

The plugin system allows data output configurations (like S3, Snowflake, Databricks, etc.) to be:
- Developed as internal modules or external packages
- Discovered automatically at startup
- Installed independently via `pip install`
- Configured through environment variables

## Architecture

### Plugin Registry

The `PluginRegistry` ([registry.py](../backend/app/data_output_configuration/registry.py)) is responsible for:
1. Discovering plugins from configured module paths
2. Discovering external plugins via Python entry points
3. Registering and managing plugin instances
4. Providing access to plugin metadata and migrations

### Plugin Base Class

All plugins inherit from `AssetProviderPlugin` ([base_schema.py](../backend/app/data_output_configuration/base_schema.py)):

```python
class AssetProviderPlugin(ORMModel, ABC):
    name: ClassVar[str]
    version: ClassVar[str] = "1.0"
    migration_file_path: ClassVar[Optional[str]] = None
    configuration_type: DataOutputTypes
    _platform_metadata: ClassVar[Optional[PlatformMetadata]] = None
```

## Creating a Plugin

### Internal Plugin

Internal plugins are part of the main codebase:

```python
# app/data_output_configuration/snowflake/schema.py
class SnowflakeDataOutput(AssetProviderPlugin):
    name: ClassVar[str] = "SnowflakeDataOutput"
    version: ClassVar[str] = "1.0"
    migration_file_path: ClassVar[str] = "app/database/alembic/versions/2026_01_28_1241-snowflake_separate_table.py"

    # Configuration fields
    database: str
    schema: str = ""
    table: str = "*"

    # UI metadata
    _platform_metadata = PlatformMetadata(
        display_name="Snowflake",
        icon_name="snowflake-logo.svg",
        platform_key="snowflake",
    )

    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        # Return form fields for UI
        pass
```

### External Plugin

External plugins are separate packages that can be installed via pip.

**Example Structure:**
```
my-plugin/
├── setup.py or pyproject.toml
├── my_plugin/
│   ├── __init__.py
│   ├── schema.py
│   └── model.py
└── README.md
```

**setup.py:**
```python
setup(
    name="my-data-output-plugin",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "data_product_portal.plugins": [
            "MyPlugin = my_plugin.schema:MyDataOutput",
        ],
    },
)
```

**pyproject.toml:**
```toml
[project.entry-points."data_product_portal.plugins"]
MyPlugin = "my_plugin.schema:MyDataOutput"
```

## Plugin Discovery

Plugins are discovered through two mechanisms:

### 1. Environment Variable Configuration

Set the `ENABLED_PLUGINS` environment variable with comma-separated plugin paths:

```bash
ENABLED_PLUGINS=app.data_output_configuration.snowflake.schema.SnowflakeDataOutput,app.data_output_configuration.databricks.schema.DatabricksDataOutput
```

If not set, the following default internal plugins are loaded:
- SnowflakeDataOutput
- DatabricksDataOutput
- GlueDataOutput
- RedshiftDataOutput

### 2. Entry Points (External Plugins)

External plugins are automatically discovered if they register the `data_product_portal.plugins` entry point.

**Installation:**
```bash
pip install my-data-output-plugin
# or for development
pip install -e /path/to/my-plugin
```

The plugin will be automatically discovered on the next portal startup.

## Testing Plugins

A test script is provided to verify plugin discovery:

```bash
cd backend
poetry run python ../plugins/test_plugins.py
```

This will:
1. Test internal plugin discovery
2. Test external plugin discovery (if installed)
3. Verify migration file paths
4. Show all registered plugins

## Plugin Components

### 1. Schema (Pydantic Model)

Defines the plugin's configuration structure and UI metadata:

```python
class MyDataOutput(AssetProviderPlugin):
    # Class variables
    name: ClassVar[str] = "MyDataOutput"
    version: ClassVar[str] = "1.0"
    migration_file_path: ClassVar[str] = "path/to/migration.py"

    # Instance fields (configuration)
    my_field: str

    # Platform metadata
    _platform_metadata = PlatformMetadata(...)

    # UI form generation
    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        return [...]
```

### 2. Model (SQLAlchemy)

Defines the database table structure:

```python
class MyDataOutput(BaseDataOutputConfiguration):
    __tablename__ = "my_data_output_configurations"

    my_field: Mapped[str] = mapped_column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "MyDataOutput",
    }
```

### 3. Migration

Creates the database table using Alembic:

```python
def upgrade():
    op.create_table(
        "my_data_output_configurations",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                 sa.ForeignKey("data_output_configurations.id", ondelete="CASCADE"),
                 primary_key=True),
        sa.Column("my_field", sa.String(), nullable=True),
        # ... other columns
    )
```

## Migration Management

Each plugin specifies its migration file path:

```python
migration_file_path: ClassVar[str] = "app/database/alembic/versions/2026_01_28_1243-my_separate_table.py"
```

To get all plugin migrations:

```python
from app.data_output_configuration.registry import PluginRegistry

migrations = PluginRegistry.get_all_migrations()
# Returns: {"MyPlugin": "path/to/migration.py", ...}
```

## API Integration

Plugins are automatically exposed through REST endpoints:

### List All Plugins
```
GET /api/v2/plugins/
```

Response:
```json
{
  "plugins": [
    {
      "plugin": "SnowflakeDataOutput",
      "display_name": "Snowflake",
      "platform": "snowflake",
      "icon_name": "snowflake-logo.svg",
      ...
    }
  ]
}
```

### Get Plugin Form
```
GET /api/v2/plugins/{plugin_name}/form
```

Response:
```json
{
  "ui_metadata": [
    {
      "name": "database",
      "label": "Database",
      "type": "select",
      "required": true,
      ...
    }
  ],
  "plugin": "SnowflakeDataOutput",
  ...
}
```

## Example: S3 External Plugin

The S3 plugin is provided as an example external plugin in `plugins/s3_plugin/`.

### Install
```bash
cd plugins/s3_plugin
pip install -e .
```

### Verify Installation
```bash
pip show data-product-portal-s3-plugin
```

### Test Discovery
```bash
cd backend
poetry run python ../plugins/test_plugins.py
```

You should see:
```
✓ S3DataOutput plugin found!
  Source: s3_plugin.schema
  Version: 1.0
  Migration: app/database/alembic/versions/2026_01_28_1243-s3_separate_table.py
```

## Best Practices

1. **Version your plugins** - Use semantic versioning
2. **Document dependencies** - Specify required portal version
3. **Test migrations** - Verify upgrade/downgrade works
4. **Provide examples** - Include sample configurations
5. **Error handling** - Graceful degradation if config missing
6. **Type safety** - Use Pydantic for validation
7. **UI clarity** - Provide helpful tooltips and labels

## Troubleshooting

### Plugin Not Discovered

1. Check entry point registration:
   ```bash
   pip show -f my-plugin | grep entry_points.txt
   ```

2. Verify plugin inherits from `AssetProviderPlugin`

3. Check logs for discovery errors:
   ```bash
   grep "Plugin registry" logs/local
   ```

### Import Errors

External plugins must have access to portal dependencies:
- Install in same environment as portal backend
- Ensure `pydantic>=2.0.0` and `sqlalchemy>=2.0.0`

### Migration Issues

1. Verify migration file path is correct
2. Ensure migration creates table with FK to `data_output_configurations`
3. Use `polymorphic_identity` matching plugin name

## Future Enhancements

- Hot-reload plugins without restart
- Plugin versioning and compatibility checks
- Sandboxed execution for untrusted plugins
- Plugin marketplace/registry
- Infrastructure provisioning hooks
