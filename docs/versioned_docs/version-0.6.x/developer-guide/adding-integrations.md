# Adding Integrations to the Data Product Portal

This guide explains the core configuration concepts and walks you through adding a new platform integration (e.g., Azure Blob Storage, AWS S3, Snowflake).

## Core Concepts

The configuration system has three layers: **Platforms**, **Platform Services**, and **Environments**. Together they define *what* infrastructure is available and *where* it is deployed.

### Platform

A **Platform** represents a cloud provider or technology vendor (e.g., AWS, Azure, Databricks, Snowflake). It is a simple entity with a name and ID.

Platforms are defined in `app/configuration/platforms/`.

### Platform Service

A **Platform Service** represents a specific service offered by a platform (e.g., S3 on AWS, Blob Storage on Azure, Unity Catalog on Databricks). Each service belongs to exactly one platform.

Key fields:
- **`name`** -- identifier used to look up the service (e.g., `s3`, `azureblob`, `snowflake`).
- **`result_string_template`** -- a Python format string rendered with the technical asset's configuration to produce a human-readable result (e.g., `{bucket}/{path}`).
- **`technical_info_template`** -- a Python format string rendered per-environment with both the technical asset configuration and environment-specific values.

Platform services are defined in `app/configuration/platforms/platform_services/`.

### Environment

An **Environment** represents a deployment stage (e.g., dev, staging, production). Environments are where the platform team configures concrete infrastructure details.

Environments are defined in `app/configuration/environments/`.

### How Defaults Work

When defining an environment, the platform team configures two types of defaults:

1. **Environment Platform Configuration** -- platform-level settings for a specific environment.
   For example, the AWS platform config for the "dev" environment might specify `account_id`, `region`, and `can_read_from`. For Azure it would be `tenant_id`, `subscription_id`, and `region`.

   Schema location: `app/configuration/environments/platform_configurations/schemas/`

2. **Environment Platform Service Configuration** -- service-level settings for a specific environment.
   For example, the S3 service config for "dev" might list available buckets with their ARNs and KMS keys. For Azure Blob, it would list available storage accounts, resource groups, and containers.

   Schema location: `app/configuration/environments/platform_service_configurations/schemas/`

There is also a **global Platform Service Configuration** (not environment-specific) that defines the list of identifiers available across all environments (e.g., `["datalake", "ingress", "egress"]`). This lives in `app/configuration/platform_service_configurations/`.

```
Platform (e.g., Azure)
│
├── Platform Service (e.g., azureblob)
│   ├── Global Service Config: ["datalake", "ingress", "egress"]
│   └── templates: result_string_template, technical_info_template
│
└── Per-Environment Configuration
    ├── Environment Platform Config (dev):
    │     tenant_id, subscription_id, region
    │
    └── Environment Platform Service Config (dev, azureblob):
          [{identifier: "datalake", storage_account_name: "...", container_name: "...", resource_group_name: "..."},
           {identifier: "ingress", ...}]
```

### Technical Assets (Data Output Configurations)

When a data product owner creates a **Technical Asset**, they pick a platform service and fill in service-specific fields (e.g., bucket name, path, schema). The technical asset configuration is what ties a data product to real infrastructure.

Technical asset configurations use a **plugin system** based on SQLAlchemy's Class Table Inheritance and Pydantic's discriminated unions. Each plugin:
- Has its own database table (for service-specific columns).
- Has a Pydantic schema with UI metadata (for form generation).
- Registers itself in a union type so the API can serialize/deserialize it.

These live in `app/data_output_configuration/<service_name>/`.

## Step-by-Step: Adding a New Integration

We'll use Azure Blob Storage as the running example. The same pattern applies to any new service.

### 1. Define the Environment Platform Configuration Schema

If your platform is new (not just a new service on an existing platform), create a platform config schema.

**File:** `app/configuration/environments/platform_configurations/schemas/azure_schema.py`

```python
from app.shared.schema import ORMModel

class AzureEnvironmentPlatformConfiguration(ORMModel):
    tenant_id: str
    subscription_id: str
    region: str
```

Register it in the `ConfigType` union in `app/configuration/environments/platform_configurations/schema_response.py`.

### 2. Define the Environment Platform Service Configuration Schema

Create a schema describing what the platform team configures per environment for your service.

**File:** `app/configuration/environments/platform_service_configurations/schemas/azure_blob_schema.py`

```python
from .config_schema import BaseEnvironmentPlatformServiceConfigurationDetail

class AzureBlobConfig(BaseEnvironmentPlatformServiceConfigurationDetail):
    storage_account_name: str
    resource_group_name: str
    container_name: str
```

Every service config must extend `BaseEnvironmentPlatformServiceConfigurationDetail`, which provides an `identifier` field used to match technical assets to their environment-specific config.

Export it in the `schemas/__init__.py` and add it to the `ConfigType` union in `app/configuration/environments/platform_service_configurations/schema_response.py`.

### 3. Create the Technical Asset Database Model

Create a new table for your service-specific columns using Class Table Inheritance.

**File:** `app/data_output_configuration/azure_blob/model.py`

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.data_output_configuration.base_model import BaseTechnicalAssetConfiguration

class AzureBlobTechnicalAssetConfiguration(BaseTechnicalAssetConfiguration):
    __tablename__ = "azure_blob_technical_asset_configurations"

    storage_account: Mapped[str] = mapped_column(String, nullable=True)
    resource_group: Mapped[str] = mapped_column(String, nullable=True)
    path: Mapped[str] = mapped_column(String, nullable=True)
    container_name: Mapped[str] = mapped_column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "AzureBlobTechnicalAssetConfiguration",
    }
```

The `polymorphic_identity` string must match the enum value you'll add in step 5.

### 4. Create the Technical Asset Plugin

This is the core of your integration. It defines configuration fields, UI metadata, template rendering, and environment config matching.

**File:** `app/data_output_configuration/azure_blob/schema.py`

```python
from typing import ClassVar, Literal, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.data_output_configuration.base_schema import (
    AssetProviderPlugin, PlatformMetadata,
    UIElementMetadata, UIElementSelect, UIElementString,
)
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.enums import UIElementType
from app.data_output_configuration.azure_blob.model import (
    AzureBlobTechnicalAssetConfiguration as AzureBlobTechnicalAssetConfigurationModel,
)
from app.data_products.schema import DataProduct
from app.users.schema import User


class AzureBlobTechnicalAssetConfiguration(AssetProviderPlugin):
    name: ClassVar[str] = "AzureBlobTechnicalAssetConfiguration"
    version: ClassVar[str] = "1.0"

    storage_account: str
    path: str = ""
    resource_group: str
    container_name: str

    configuration_type: Literal[DataOutputTypes.AzureBlobTechnicalAssetConfiguration]

    _platform_metadata = PlatformMetadata(
        display_name="Blob",
        icon_name="azure-storage-account-logo.svg",
        platform_key="azureblob",       # must match the platform_services.name in DB
        parent_platform="azure",         # groups this under the Azure platform in UI
        result_label="Resulting path",
        result_tooltip="The path you can access through this technical asset",
        detailed_name="Path",
    )

    class Meta:
        orm_model = AzureBlobTechnicalAssetConfigurationModel

    def validate_configuration(self, data_product: DataProduct):
        pass  # Add validation logic if needed

    def on_create(self):
        pass  # Hook called when a technical asset is created

    @classmethod
    def get_url(cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None) -> str:
        return "https://portal.azure.com/"

    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        base_metadata = super().get_ui_metadata(db)
        base_metadata += [
            UIElementMetadata(
                name="storage_account",
                label="Storage Account",
                type=UIElementType.Select,
                required=True,
                select=UIElementSelect(options=cls.get_platform_options(db)),
            ),
            UIElementMetadata(
                name="container_name",
                label="Container",
                required=True,
                type=UIElementType.Select,
                select=UIElementSelect(options=cls.get_platform_options(db)),
            ),
            # ... more fields
        ]
        return base_metadata
```

Key things to implement in your plugin:
- **`_platform_metadata`** -- controls how the service appears in the UI. Set `platform_key` to match the `platform_services.name` in the database so the options dropdown can look up the global config.
- **`get_ui_metadata()`** -- returns a list of form fields. Use `get_platform_options(db)` to populate select dropdowns from the global `PlatformServiceConfiguration`.
- **`get_configuration()`** -- given a list of environment configs, return the one matching this technical asset (typically matched by `identifier`).
- **`render_template()`** -- override if you need to post-process template output (e.g., S3 strips empty path segments, Snowflake replaces hyphens).
- **`get_url()`** -- returns a link to the resource in the cloud provider's console.

### 5. Register the Plugin

**a)** Add an entry to the `DataOutputTypes` enum:

**File:** `app/data_output_configuration/data_output_types.py`
```python
class DataOutputTypes(str, Enum):
    # ... existing types
    AzureBlobTechnicalAssetConfiguration = "AzureBlobTechnicalAssetConfiguration"
```

**b)** Add to the `DataOutputs` union and `DataOutputMap`:

**File:** `app/data_output_configuration/schema_union.py`

**c)** Export from `app/data_output_configuration/__init__.py`

### 6. Create a Database Migration

Generate an Alembic migration for the new table:

```bash
cd backend
poetry run alembic revision --autogenerate -m "add_azure_blob_technical_asset"
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

### 7. Seed Data

Add seed data in `sample_data.sql` for:
- The **platform** (if new): `INSERT INTO platforms ...`
- The **platform service**: `INSERT INTO platform_services ...` with `result_string_template` and `technical_info_template`
- The **global service config**: `INSERT INTO platform_service_configs ...` with the list of available identifiers (e.g., `["datalake", "ingress", "egress"]`)
- **Environment platform config**: `INSERT INTO env_platform_configs ...` with platform credentials per environment
- **Environment service config**: `INSERT INTO env_platform_service_configs ...` with the concrete infrastructure details per environment

### 8. Backend: Enable the Plugin

Update `backend/app/settings.py` to add your plugin to the list of available plugins.

```python
class Settings(BaseSettings):
    # ...
    ENABLED_PLUGINS: list[str] = [
        # ... existing plugins
        "PostgreSQLTechnicalAssetConfiguration",
    ]
```

#### Enabling via Environment Variables

Alternatively, you can override the enabled plugins using the `ENABLED_PLUGINS` environment variable. This is useful for different deployments or demo environments. The value should be a JSON-encoded list of strings.

In your `.env` or `compose.yaml`:

```env
ENABLED_PLUGINS='["PostgreSQLTechnicalAssetConfiguration", "S3TechnicalAssetConfiguration"]'
```

---

### 9. Frontend: Add Assets and Update Generated Code

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

## Summary

| Concept | What it represents | Who configures it | Where in code |
|---|---|---|---|
| Platform | Cloud provider (AWS, Azure) | Admin | `app/configuration/platforms/` |
| Platform Service | Service on a platform (S3, Blob) | Admin | `app/configuration/platforms/platform_services/` |
| Environment | Deployment stage (dev, prod) | Platform team | `app/configuration/environments/` |
| Env Platform Config | Platform credentials per env | Platform team | `app/configuration/environments/platform_configurations/` |
| Env Platform Service Config | Available resources per env | Platform team | `app/configuration/environments/platform_service_configurations/` |
| Global Service Config | Available identifiers (all envs) | Platform team | `app/configuration/platform_service_configurations/` |
| Technical Asset Plugin | Data output type for products | Developer | `app/data_output_configuration/<service>/` |

---

## Database & Service Architecture

Understanding the underlying data model helps when debugging integration issues or seeding a new environment.

### Table Overview

| Table | Purpose |
|---|---|
| `platforms` | Top-level platform identity (e.g. `AWS`, `PostgreSQL`, `OSI`) |
| `platform_services` | Services offered by a platform (e.g. `S3`, `Glue`). Holds `result_string_template` and `technical_info_template`. |
| `platform_service_configs` | Available options for a service (e.g. the list of S3 bucket names). Required for every service, even if empty. The names defined here are used to render technical asset forms via `get_platform_options`, and are often linked by an `"identifier"` field in `env_platform_service_configs`. |
| `environments` | Deployment environments (e.g. `development`, `production`) |
| `env_platform_configs` | Environment-specific details at the platform level (e.g. AWS account details, Snowflake credentials). |
| `env_platform_service_configs` | Environment-specific connection details for a platform/service combination. Typically used alongside `platform_service_configs` — the entries here are matched by `"identifier"` in JSON to the options listed there. The correct config is looked up in each plugin's `technical_info` method. |
| `data_output_configurations` | Polymorphic base table for technical asset configurations. Each plugin has its own child table joined on `id`. |
| `data_outputs` | The technical asset record itself — links a data product to a `platform`, `service`, and `data_output_configurations` row |

### How Templates Work

`platform_services.result_string_template` and `technical_info_template` are Python `.format()`-style strings rendered using the field names from the plugin's Pydantic schema. For example:

- PostgreSQL: `"{database}.{schema}.{table}"` — fields `database`, `schema`, `table` come from `PostgreSQLTechnicalAssetConfiguration`
- OSI Semantic Model: `"{model_name}"` — field `model_name` comes from `OSISemanticModelTechnicalAssetConfiguration`

### `has_environments` Flag

The `has_environments` flag on `PlatformMetadata` controls two things: whether the plugin needs environment-specific platform configuration, and whether the environment selector dropdown is shown on the platform tile in the UI.

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
