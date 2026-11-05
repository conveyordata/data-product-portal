import re
from collections import Counter
from enum import Enum
from typing import Any, ClassVar, Optional, Self
from uuid import UUID

from pydantic import model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.configuration.environments.platform_service_configurations.schema_response import (
    PostgreSQLConfig,
)
from app.data_products.technical_assets.model import TechnicalAsset
from app.technical_asset_configuration.base_schema import (
    EnvironmentConfigurationError,
    EnvironmentFieldError,
    EnvironmentSettings,
    PluginContext,
    FieldDependency,
    PlatformMetadata,
    SelectOption,
    TechnicalAssetPlugin,
    UIElementMetadata,
    UIElementRadio,
    UIElementSelect,
    UIElementString,
    env_field,
)
from app.technical_asset_configuration.enums import AccessGranularity, UIElementType
from portal_plugins.postgresql.model import (
    NAME,
)
from portal_plugins.postgresql.model import (
    PostgreSQLEnvironmentConfiguration as PostgreSQLEnvironmentConfigurationModel,
)
from portal_plugins.postgresql.model import (
    PostgreSQLTechnicalAssetConfiguration as PostgreSQLTechnicalAssetConfigurationModel,
)

INSTANCE_NAME_PATTERN = re.compile(r"[a-z][a-z0-9_-]{0,62}")


class EngineVersion(str, Enum):
    v16 = "16"
    v17 = "17"
    v18 = "18"


class Size(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"


class StorageGb(int, Enum):
    gb20 = 20
    gb50 = 50
    gb100 = 100


class PostgreSQLEnvironmentConfigurationSchema(EnvironmentSettings):
    engine_version: EngineVersion = env_field(
        label="Engine version",
        tooltip="The PostgreSQL major version this Environment runs",
        type=UIElementType.Select,
        options=[
            SelectOption(label="16", value=EngineVersion.v16),
            SelectOption(label="17", value=EngineVersion.v17),
            SelectOption(label="18", value=EngineVersion.v18),
        ],
        default=EngineVersion.v17,
        default_per_environment={
            "prd": EngineVersion.v16,
        },
        disabled_per_environment={
            "prd": {EngineVersion.v18},
        },
    )
    size: Size = env_field(
        label="Size",
        tooltip="Compute size of the database instance in this Environment",
        type=UIElementType.Select,
        options=[
            SelectOption(label="Small", value=Size.small),
            SelectOption(label="Medium", value=Size.medium),
            SelectOption(label="Large", value=Size.large),
        ],
        default=Size.small,
        default_per_environment={
            "prd": Size.medium,
        },
        disabled_per_environment={
            "dev": {Size.large},
        },
    )
    storage_gb: StorageGb = env_field(
        label="Storage (GB)",
        tooltip="Disk space reserved for the database instance, in GB",
        type=UIElementType.Select,
        options=[
            SelectOption(label="20", value=StorageGb.gb20),
            SelectOption(label="50", value=StorageGb.gb50),
            SelectOption(label="100", value=StorageGb.gb100),
        ],
        default=StorageGb.gb20,
        default_per_environment={
            "prd": StorageGb.gb50,
        },
    )
    instance_name: str = env_field(
        label="Instance name",
        tooltip="Name of the database instance in this Environment. Use lowercase letters, digits, underscores and hyphens, starting with a letter",
        type=UIElementType.String,
        default="{database:.16}-{schema:.36}-{environment}",
        default_per_environment={
            "prd": "{database:.16}-{schema:.36}",
        },
    )

    class Meta:
        orm_model = PostgreSQLEnvironmentConfigurationModel


class PostgreSQLTechnicalAssetConfiguration(TechnicalAssetPlugin):
    name: ClassVar[str] = NAME
    version: ClassVar[str] = "1.0"
    environment_configuration: ClassVar[type[EnvironmentSettings]] = (
        PostgreSQLEnvironmentConfigurationSchema
    )

    database: str
    schema: str = ""
    table: str = "*"
    access_granularity: AccessGranularity

    _platform_metadata = PlatformMetadata(
        result_string_template="{database}.{schema}.{table}",
        display_name="PostgreSQL",
        icon_name="postgresql-logo.svg",
        icon_package="portal_plugins.postgresql",
        platform_key="postgresql",
        parent_platform=None,
        result_label="Resulting table",
        result_tooltip="The table you can access through this technical asset",
        detailed_name="Schema",
    )

    class Meta:
        orm_model = PostgreSQLTechnicalAssetConfigurationModel

    @model_validator(mode="after")
    def validate_paths(self) -> Self:
        if self.access_granularity == AccessGranularity.Schema:
            self.table = "*"
        return self

    def validate_configuration(self, context: PluginContext, db: Session):
        if not self.database.startswith(context.data_product.namespace):
            raise ValueError("Invalid database specified")

    def validate_environment_configuration(
        self,
        values: dict[UUID, dict[str, Any]],
        context: PluginContext,
        db: Session,
    ) -> None:
        names = {
            environment_id: cell["instance_name"]
            for environment_id, cell in values.items()
        }
        counts = Counter(names.values())
        taken = set(
            db.scalars(
                select(PostgreSQLEnvironmentConfigurationModel.instance_name)
                .join(
                    TechnicalAsset,
                    TechnicalAsset.configuration_id
                    == PostgreSQLEnvironmentConfigurationModel.configuration_id,
                )
                .where(
                    PostgreSQLEnvironmentConfigurationModel.instance_name.in_(
                        names.values()
                    ),
                    TechnicalAsset.id.is_distinct_from(context.technical_asset.id),
                )
            )
        )
        errors = [
            EnvironmentFieldError(
                environment_id=environment_id, field="instance_name", message=message
            )
            for environment_id, name in names.items()
            for condition, message in [
                (
                    not INSTANCE_NAME_PATTERN.fullmatch(name),
                    "Use lowercase letters, digits, underscores and hyphens, starting with a letter (max 63)",
                ),
                (
                    counts[name] > 1,
                    "Instance name is used in another Environment of this Technical Asset",
                ),
                (
                    name in taken,
                    "Instance name is already used by another Technical Asset",
                ),
            ]
            if condition
        ]
        if errors:
            raise EnvironmentConfigurationError(errors)

    def render_template(self, template, **context):
        return ".".join(
            [
                part.rstrip("_")
                for part in super().render_template(template, **context).split(".")
            ]
        )

    def get_configuration(
        self, configs: list[PostgreSQLConfig]
    ) -> Optional[PostgreSQLConfig]:
        # Implementation depends on the exact PostgreSQL config type added
        return next(
            (config for config in configs if config.identifier == self.database), None
        )

    @classmethod
    def get_url(cls, id, db, actor, environment=None) -> str:
        # Implementation for PostgreSQL URL
        return ""

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
            UIElementMetadata(
                name="schema",
                type=UIElementType.String,
                label="Schema",
                tooltip="The name of the schema to give write access to. Defaults to data product namespace",
                required=True,
            ),
            UIElementMetadata(
                name="access_granularity",
                label="Access granularity",
                type=UIElementType.Radio,
                tooltip="Give write access to the entire schema or a single table",
                required=True,
                radio=UIElementRadio(
                    initial_value=AccessGranularity.Schema,
                    options=[
                        SelectOption(
                            label="Schema level", value=AccessGranularity.Schema
                        ),
                        SelectOption(
                            label="Table level", value=AccessGranularity.Table
                        ),
                    ],
                ),
            ),
            UIElementMetadata(
                name="table",
                label="Table",
                type=UIElementType.String,
                tooltip="The name of the table to give write access to",
                required=True,
                string=UIElementString(initial_value="*"),
                depends_on=[
                    FieldDependency(
                        field_name="access_granularity", value=AccessGranularity.Table
                    )
                ],
            ),
        ]
        return base_metadata
