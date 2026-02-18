import json
from typing import ClassVar, Literal, Optional, Self

from fastapi import HTTPException, status
from pydantic import model_validator
from sqlalchemy.orm import Session

from app.configuration.environments.platform_configurations.service import (
    EnvironmentPlatformConfigurationService,
)
from app.configuration.environments.platform_service_configurations.schemas import (
    DatabricksConfig,
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
from app.data_output_configuration.databricks.model import (
    DatabricksTechnicalAssetConfiguration as DatabricksTechnicalAssetConfigurationModel,
)
from app.data_output_configuration.enums import AccessGranularity, UIElementType
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.schema import DataProduct


class DatabricksTechnicalAssetConfiguration(AssetProviderPlugin):
    name: ClassVar[str] = "DatabricksTechnicalAssetConfiguration"
    version: ClassVar[str] = "1.0"

    catalog: str
    schema: str = ""
    configuration_type: Literal[DataOutputTypes.DatabricksTechnicalAssetConfiguration]
    table: str = "*"
    bucket_identifier: str = ""
    catalog_path: str = ""
    table_path: str = ""
    access_granularity: AccessGranularity

    _platform_metadata = PlatformMetadata(
        display_name="Databricks",
        icon_name="databricks-logo.svg",
        platform_key="databricks",
        parent_platform=None,
        result_label="Resulting table",
        result_tooltip="The table you can access through this technical asset",
        detailed_name="Schema",
    )

    class Meta:
        orm_model = DatabricksTechnicalAssetConfigurationModel

    @model_validator(mode="after")
    def validate_paths(self) -> Self:
        if not self.catalog_path:
            self.catalog_path = self.catalog
        if not self.table_path:
            self.table_path = self.table
        if self.access_granularity == AccessGranularity.Schema:
            self.table = "*"
        return self

    def validate_configuration(self, data_product: DataProduct):
        # If product aligned
        if not self.catalog.startswith(data_product.namespace):
            raise ValueError("Invalid catalog specified")

    def on_create(self):
        pass

    def get_configuration(
        self, configs: list[DatabricksConfig]
    ) -> Optional[DatabricksConfig]:
        return next(
            (config for config in configs if config.identifier == self.catalog), None
        )

    @classmethod
    def get_url(cls, id, db, actor, environment=None) -> str:
        platform_config = EnvironmentPlatformConfigurationService(
            db
        ).get_env_platform_config(environment, "Databricks")
        data_product = db.get(DataProductModel, id)
        config = json.loads(platform_config)["workspace_urls"]
        if str(data_product.domain_id) not in config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Workspace not configured for domain {data_product.domain.name}"
                ),
            )
        return config[str(data_product.domain_id)]

    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        base_metadata = super().get_ui_metadata(db)
        base_metadata += [
            UIElementMetadata(
                name="catalog",
                label="Catalog",
                type=UIElementType.Select,
                required=True,
                use_namespace_when_not_source_aligned=True,
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
