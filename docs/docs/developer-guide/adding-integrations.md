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
