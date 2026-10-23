from typing import ClassVar, Optional, Self

from pydantic import model_validator
from sqlalchemy.orm import Session

from app.configuration.environments.platform_service_configurations.schema_response import (
    PostgreSQLConfig,
)
from app.technical_asset_configuration.base_schema import (
    PluginContext,
    FieldDependency,
    PlatformMetadata,
    SelectOption,
    TechnicalAssetPlugin,
    UIElementMetadata,
    UIElementRadio,
    UIElementSelect,
    UIElementString,
)
from app.technical_asset_configuration.enums import AccessGranularity, UIElementType
from portal_plugins.postgresql.model import (
    NAME,
)
from portal_plugins.postgresql.model import (
    PostgreSQLTechnicalAssetConfiguration as PostgreSQLTechnicalAssetConfigurationModel,
)


class PostgreSQLTechnicalAssetConfiguration(TechnicalAssetPlugin):
    name: ClassVar[str] = NAME
    version: ClassVar[str] = "1.0"

    database: str
    schema: str = ""
    table: str = "*"
    access_granularity: AccessGranularity
    engine_version: str = "16"
    size: str = "small"
    storage_gb: str = "20"

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
            _overridable_select(
                "engine_version", "Engine version", ["15", "16", "17"], "16"
            ),
            _overridable_select("size", "Size", ["small", "medium", "large"], "small"),
            _overridable_select(
                "storage_gb", "Storage (GB)", ["20", "50", "100"], "20"
            ),
        ]
        return base_metadata


def _overridable_select(
    name: str, label: str, values: list[str], default: str
) -> UIElementMetadata:
    return UIElementMetadata(
        name=name,
        label=label,
        type=UIElementType.Select,
        required=True,
        environment_overridable=True,
        select=UIElementSelect(
            initial_value=default,
            options=[SelectOption(label=value, value=value) for value in values],
        ),
    )
