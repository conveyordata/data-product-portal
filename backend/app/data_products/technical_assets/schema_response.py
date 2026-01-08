from typing import Optional, Sequence
from uuid import UUID
from warnings import deprecated

from pydantic import Field, computed_field

from app.configuration.environments.platform_service_configurations.schema_response import (
    EnvironmentConfigsGetItem,
)
from app.configuration.platforms.platform_services.schema import PlatformService
from app.configuration.tags.schema import Tag
from app.data_output_configuration.base_schema import UIElementMetadata
from app.data_output_configuration.schema_union import DataOutputConfiguration
from app.data_products.output_port_technical_assets_link.schema import (
    DataOutputDatasetAssociation,
    TechnicalAssetOutputPortAssociation,
)
from app.data_products.output_ports.schema import Dataset, OutputPort
from app.data_products.schema import DataProduct
from app.data_products.technical_assets.status import TechnicalAssetStatus
from app.shared.schema import ORMModel


class TechnicalInfo(ORMModel):
    environment_id: UUID
    environment: str
    info: Optional[str]


class BaseTechnicalAssetGet(ORMModel):
    id: UUID
    name: str
    description: str
    namespace: str
    owner_id: UUID
    platform_id: UUID
    service_id: UUID
    status: TechnicalAssetStatus
    sourceAligned: Optional[bool]

    # Nested schemas
    configuration: DataOutputConfiguration
    owner: DataProduct

    # Excluded
    service: PlatformService = Field(exclude=True)
    environment_configurations: list[EnvironmentConfigsGetItem] = Field(exclude=True)

    @computed_field
    def result_string(self) -> str:
        return self.configuration.render_template(self.service.result_string_template)

    @computed_field
    def technical_info(self) -> list[TechnicalInfo]:
        technical_info_list = []
        for environment_configuration in self.environment_configurations:
            configuration = self.configuration.get_configuration(
                environment_configuration.config
            )
            context = configuration.model_dump() if configuration else {}
            context["environment"] = environment_configuration.environment.acronym

            info = self.configuration.render_template(
                self.service.technical_info_template, **context
            )
            technical_info_list.append(
                TechnicalInfo(
                    environment_id=environment_configuration.environment.id,
                    environment=environment_configuration.environment.name,
                    info=info,
                )
            )
        return technical_info_list


@deprecated("Use BaseTechnicalAssetGet instead")
class BaseDataOutputGet(BaseTechnicalAssetGet):
    pass


class OutputPortLink(TechnicalAssetOutputPortAssociation):
    output: OutputPort


@deprecated("OutputPortLink instead")
class DatasetLink(DataOutputDatasetAssociation):
    # Nested schemas
    dataset: Dataset

    def convert(self) -> OutputPortLink:
        base = self.model_dump(exclude={"dataset", "dataset_id", "data_output_id"})
        return OutputPortLink(
            **base,
            output_port_id=self.dataset_id,
            technical_asset_id=self.data_output_id,
            output=self.dataset.convert(),
        )


class GetTechnicalAssetsResponseItem(BaseTechnicalAssetGet):
    # Nested schemas
    output_port_links: list[OutputPortLink]
    tags: list[Tag]


@deprecated("Use GetTechnicalAssetsResponseItem instead")
class DataOutputGet(BaseDataOutputGet):
    # Nested schemas
    dataset_links: list[DatasetLink]
    tags: list[Tag]

    def convert(self) -> GetTechnicalAssetsResponseItem:
        base_data = self.model_dump(exclude={"dataset_links"})
        return GetTechnicalAssetsResponseItem(
            **base_data,
            output_port_links=[dl.convert() for dl in self.dataset_links],
            service=self.service,
            environment_configurations=self.environment_configurations,
        )


class DataOutputsGet(DataOutputGet):
    pass


class GetTechnicalAssetsResponse(ORMModel):
    technical_assets: Sequence[GetTechnicalAssetsResponseItem]


class UpdateTechnicalAssetResponse(ORMModel):
    id: UUID


class PlatformTile(ORMModel):
    """Represents a platform tile in the UI"""

    label: str
    value: str  # platform identifier
    icon_name: str
    has_menu: bool = True
    has_config: bool = True
    children: list["PlatformTile"] = []


class UIElementMetadataResponse(ORMModel):
    ui_metadata: Sequence[UIElementMetadata]
    plugin: str
    result_label: str = "Resulting path"
    result_tooltip: str = "The path you can access through this technical asset"
    platform: str  # e.g., "s3", "redshift", "snowflake"
    display_name: str  # Display name for the platform tile
    icon_name: str  # Icon filename (e.g., "s3-logo.svg")
    parent_platform: Optional[str] = None  # e.g., "aws" for s3, redshift, glue
    platform_tile: Optional[PlatformTile] = None  # Complete tile structure
