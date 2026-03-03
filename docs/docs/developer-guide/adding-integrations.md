---
id: adding-integrations
title: Adding New Integrations
sidebar_label: Adding Integrations
sidebar_position: 7
---

# Adding New Integrations

The Data Product Portal provides an extensible plugin system to connect and configure output ports for different data platforms (e.g., AWS S3, Snowflake, Databricks, PostgreSQL).

If you want to add support for a new data platform or integration type, follow these steps to implement the necessary backend and frontend components.

## Overview of the Process

Adding a new integration requires modifying multiple parts of the application:
1. **Backend schemas and models:** Defining how the configuration is structured and stored.
2. **Backend plugin configuration:** Registering the new output type.
3. **Database migrations:** Creating tables to store the new configuration type.
4. **Environment variables:** Enabling the new integration plugin.
5. **Frontend components:** Adding icons and configuration forms.

---

## 1. Backend: Define Schemas and Models

First, create a new directory for your integration under `backend/app/data_output_configuration/`.
For example, if adding `postgresql`, you would create `backend/app/data_output_configuration/postgresql/`.

Inside this directory, create the following files:

### `schema.py`
Define the Pydantic schema for your new integration.

```python
from typing import ClassVar, Literal, Optional, Self

from pydantic import model_validator
from sqlalchemy.orm import Session

from app.configuration.environments.platform_service_configurations.schema_response import (
    PostgreSQLConfig,
)
from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    FieldDependency,
    PlatformMetadata,
    SelectOption,
    UIElementMetadata,
    UIElementRadio,
    UIElementSelect,
    UIElementString,
)
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.enums import AccessGranularity, UIElementType
from app.data_output_configuration.postgresql.model import (
    PostgreSQLTechnicalAssetConfiguration as PostgreSQLTechnicalAssetConfigurationModel,
)

class PostgreSQLTechnicalAssetConfiguration(AssetProviderPlugin):
    name: ClassVar[str] = "PostgreSQLTechnicalAssetConfiguration"
    version: ClassVar[str] = "1.0"

    database: str
    schema: str = ""
    configuration_type: Literal[DataOutputTypes.PostgreSQLTechnicalAssetConfiguration]
    table: str = "*"
    access_granularity: AccessGranularity

    _platform_metadata = PlatformMetadata(
        display_name="PostgreSQL",
        icon_name="postgresql-logo.svg",
        platform_key="postgresql",
        parent_platform=None,
        result_label="Resulting table",
        result_tooltip="The table you can access through this technical asset",
        detailed_name="Schema",
    )

    class Meta:
        orm_model = PostgreSQLTechnicalAssetConfigurationModel

    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        base_metadata = super().get_ui_metadata(db)
        base_metadata += [
            UIElementMetadata(
                name="database",
                label="Database",
                type=UIElementType.Select,
                required=True,
                use_namespace_when_not_source_aligned=True,
                options=cls.get_platform_options(db),
                select=UIElementSelect(options=cls.get_platform_options(db)),
            ),
            # ... other UI elements
        ]
        return base_metadata
```

### `model.py`
Define the SQLAlchemy ORM model to store the configurations.

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.data_output_configuration.base_model import BaseTechnicalAssetConfiguration

class PostgreSQLTechnicalAssetConfiguration(BaseTechnicalAssetConfiguration):
    __tablename__ = "postgresql_technical_asset_configurations"

    database: Mapped[str] = mapped_column(String, nullable=True)
    schema: Mapped[str] = mapped_column(String, nullable=True)
    table: Mapped[str] = mapped_column(String, nullable=True)
    access_granularity: Mapped[str] = mapped_column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "PostgreSQLTechnicalAssetConfiguration",
    }
```

---

## 2. Backend: Register the Output Type

Update the global configuration files to include your new type.

### `backend/app/data_output_configuration/data_output_types.py`
Add your type to the `DataOutputTypes` Enum:

```python
class DataOutputTypes(str, Enum):
    # ... existing types
    PostgreSQLTechnicalAssetConfiguration = "PostgreSQLTechnicalAssetConfiguration"
```

### `backend/app/data_output_configuration/__init__.py`
Export your new schema:

```python
from .postgresql.schema import PostgreSQLTechnicalAssetConfiguration

__all__ = [
    # ... existing exports
    "PostgreSQLTechnicalAssetConfiguration",
]
```

### `backend/app/data_output_configuration/schema_union.py`
Add your schema to the unions and mapping dictionary:

```python
from app.data_output_configuration.postgresql.schema import PostgreSQLTechnicalAssetConfiguration

DataOutputs = Union[
    # ... existing
    PostgreSQLTechnicalAssetConfiguration,
]

DataOutputMap = {
    # ... existing
    DataOutputTypes.PostgreSQLTechnicalAssetConfiguration: PostgreSQLTechnicalAssetConfiguration,
}
```

### `backend/app/configuration/environments/platform_service_configurations/schema_response.py`
If your integration requires specific environment platform service configurations, define a schema for it (e.g., `PostgreSQLConfig`) and add it to `ConfigType`:

```python
from app.configuration.environments.platform_service_configurations.schemas.postgresql_schema import PostgreSQLConfig

ConfigType = (
    # ... existing
    | PostgreSQLConfig
)
```

---

## 3. Database: Create Alembic Migrations

Since the application uses a polymorphic table structure for configurations, you need to create a dedicated table for your new integration's configuration.

Run the Alembic revision command (or manually create a file in `backend/app/database/alembic/versions/`):

```bash
docker compose exec backend alembic revision -m "postgresql_separate_table"
```

Update the migration script to create the new table. It must inherit from the base `data_output_configurations` table via a foreign key `id`:

```python
def upgrade() -> None:
    op.create_table(
        "postgresql_technical_asset_configurations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("data_output_configurations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("database", sa.String(), nullable=True),
        sa.Column("schema", sa.String(), nullable=True),
        sa.Column("table", sa.String(), nullable=True),
        # ... other columns
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime(timezone=False), nullable=True),
    )
```

---

## 4. Backend: Enable the Plugin

Update `backend/app/settings.py` to add your plugin to the list of available plugins.

```python
class Settings(BaseSettings):
    # ...
    ENABLED_PLUGINS: list[str] = [
        # ... existing plugins
        "PostgreSQLTechnicalAssetConfiguration",
    ]
```

### Enabling via Environment Variables

Alternatively, you can override the enabled plugins using the `ENABLED_PLUGINS` environment variable. This is useful for different deployments or demo environments. The value should be a JSON-encoded list of strings.

In your `.env` or `compose.yaml`:

```env
ENABLED_PLUGINS='["PostgreSQLTechnicalAssetConfiguration", "S3TechnicalAssetConfiguration"]'
```

---

## 5. Frontend: Add Assets and Update Generated Code

To display the integration correctly in the UI:

1. **Icons:** Add an SVG logo (e.g., `postgresql-logo.svg`) and a border icon (e.g., `postgresql-border-icon.svg`) to `frontend/src/assets/icons/`.
2. **Code Generation:** Because the OpenAPI spec has changed (due to the backend modifications), you need to regenerate the frontend API client.

Ensure your backend is running, then generate the new spec and update the frontend:

```bash
# Export the new OpenAPI spec
task update:open-api-spec

# Regenerate frontend API clients
cd frontend
npm run generate-api
```

This will automatically update the files in `frontend/src/store/api/services/generated/`.

---

## Conclusion

By following these steps, you have successfully:
- Modeled the integration schema and configuration tables
- Registered the type so the portal recognizes it
- Added the database migrations to store configuration data
- Enabled the plugin in the application settings
- Generated the updated frontend models and added styling assets

Your new integration will now be available when configuring data output ports in the Data Product Portal.

---

## Database & Service Architecture

Understanding the underlying data model helps when debugging integration issues or seeding a new environment.

### Table Overview

| Table | Purpose |
|---|---|
| `platforms` | Top-level platform identity (e.g. `AWS`, `PostgreSQL`, `OSI`) |
| `platform_services` | Services offered by a platform (e.g. `S3`, `Glue`). Holds `result_string_template` and `technical_info_template`. |
| `platform_service_configs` | Available options for a service (e.g. the list of S3 bucket names). Required for every service, even if empty. |
| `environments` | Deployment environments (e.g. `development`, `production`) |
| `env_platform_service_configs` | Environment-specific connection details for a platform/service combination (e.g. host, credentials) |
| `data_output_configurations` | Polymorphic base table for technical asset configurations. Each plugin has its own child table joined on `id`. |
| `data_outputs` | The technical asset record itself — links a data product to a `platform`, `service`, and `data_output_configurations` row |

### How Templates Work

`platform_services.result_string_template` and `technical_info_template` are Python `.format()`-style strings rendered using the field names from the plugin's Pydantic schema. For example:

- PostgreSQL: `"{database}.{schema}.{table}"` — fields `database`, `schema`, `table` come from `PostgreSQLTechnicalAssetConfiguration`
- OSI Semantic Model: `"{model_name}"` — field `model_name` comes from `OSISemanticModelTechnicalAssetConfiguration`

### `has_environments` Flag

The `has_environments` flag on `PlatformMetadata` controls whether the plugin needs environment-specific platform configuration:

| `has_environments` | `env_platform_service_configs` needed? | `platform_service_configs` needed? |
|---|---|---|
| `True` (default) | Yes — connection details per environment | Yes — list of available options (e.g. buckets) |
| `False` | No | **Yes — still required, use `'[]'` as config** |

The `platform_service_configs` row is always required because the frontend uses it to populate `platformConfig`, which is the source of truth for `platform_id` and `service_id` in the creation form. Without it, the platform tile will appear in the UI but the form will silently fail to set these IDs.

---

## Critical Naming Conventions

The frontend resolves `platform_id` and `service_id` through two independent lookups, both driven by names. Getting these wrong causes silent failures during technical asset creation.

### 1. `platform.name` must equal `display_name`

The `platform_id` form field is populated by matching:
```
platformConfig.find(config => config.platform.name === tile.label)
```
`tile.label` comes from `_platform_metadata.display_name`. So:

```python
# In schema.py
_platform_metadata = PlatformMetadata(display_name="OSI", ...)

# In seed SQL / DB
INSERT INTO platforms (name) VALUES ('OSI')  -- must match display_name exactly
```

### 2. `service.name.toLowerCase()` must equal `platform_key`

The `service_id` is looked up via a map keyed by `service.name.toLowerCase()`, using `platform_key` as the lookup key:

```python
# In schema.py
_platform_metadata = PlatformMetadata(platform_key="osi", ...)

# In seed SQL / DB
INSERT INTO platform_services (name) VALUES ('OSI')  -- 'OSI'.toLowerCase() == 'osi' == platform_key ✓
```

A mismatch here means the `service_id` is never set, and the subsequent `render_technical_asset_access_path` call returns a 422.

### Summary Checklist for a New Integration

When seeding a new environment (e.g. `demo/basic/portal_seed.sql`), ensure all three rows exist and names align:

```sql
-- 1. Platform — name must match _platform_metadata.display_name
INSERT INTO platforms (name) VALUES ('MyPlatform');

-- 2. Service — name.toLowerCase() must match _platform_metadata.platform_key
INSERT INTO platform_services (name, platform_id, result_string_template, technical_info_template)
VALUES ('myplatform', <platform_id>, '{field_name}', '{other_field}');

-- 3. Config — required even if empty; without this the frontend cannot resolve platform_id/service_id
INSERT INTO platform_service_configs (platform_id, service_id, config)
VALUES (<platform_id>, <service_id>, '[]');

-- 4. Only if has_environments=True: environment-specific connection details
INSERT INTO env_platform_service_configs (environment_id, platform_id, service_id, config)
VALUES (<env_id>, <platform_id>, <service_id>, '[{...connection details...}]');
```
