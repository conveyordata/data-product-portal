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

## Technical Assets (Data Output Configurations)

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

### 4. Create the Technical Asset Pydantic Schema (Plugin)

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
    AzureBlobTechnicalAssetConfiguration = "AzureBlobTechnicalAssetConfiguration"
    # ...
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

### 7. Seed Data

Add seed data in `sample_data.sql` for:
- The **platform** (if new): `INSERT INTO platforms ...`
- The **platform service**: `INSERT INTO platform_services ...` with `result_string_template` and `technical_info_template`
- The **global service config**: `INSERT INTO platform_service_configs ...` with the list of available identifiers (e.g., `["datalake", "ingress", "egress"]`)
- **Environment platform config**: `INSERT INTO env_platform_configs ...` with platform credentials per environment
- **Environment service config**: `INSERT INTO env_platform_service_configs ...` with the concrete infrastructure details per environment

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
