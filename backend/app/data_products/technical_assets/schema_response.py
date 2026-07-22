from typing import Optional, Sequence
from uuid import UUID

from pydantic import Field, computed_field

from app.configuration.environments.platform_service_configurations.schema_response import (
    EnvironmentConfigsGetItem,
)
from app.configuration.platforms.platform_services.schema import PlatformService
from app.configuration.tags.schema import Tag
from app.data_products.output_port_technical_assets_link.schema import (
    TechnicalAssetOutputPortAssociation,
)
from app.data_products.output_ports.schema import OutputPort
from app.data_products.schema import DataProduct
from app.data_products.technical_assets.enums import TechnicalMapping
from app.data_products.technical_assets.status import TechnicalAssetStatus
from app.shared.schema import ORMModel
from app.technical_asset_configuration.schema_union import DataOutputConfiguration


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
    technical_mapping: TechnicalMapping

    configuration: DataOutputConfiguration
    owner: DataProduct

    service: PlatformService = Field(exclude=True)
    environment_configurations: list[EnvironmentConfigsGetItem] = Field(exclude=True)

    @computed_field(
        description="DEPRECATED: Use 'technical_mapping' instead. "
        "This field will be removed in a future version."
    )
    def sourceAligned(self) -> bool:
        """Backwards compatibility: convert technical_mapping back to source_aligned."""
        return self.technical_mapping == TechnicalMapping.Custom

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


class OutputPortLink(TechnicalAssetOutputPortAssociation):
    output_port: OutputPort


class GetTechnicalAssetsResponseItem(BaseTechnicalAssetGet):
    output_port_links: list[OutputPortLink] = Field(validation_alias="dataset_links")
    tags: list[Tag]


class GetTechnicalAssetsResponse(ORMModel):
    technical_assets: Sequence[GetTechnicalAssetsResponseItem]


class UpdateTechnicalAssetResponse(ORMModel):
    id: UUID


class CreateTechnicalAssetResponse(ORMModel):
    id: UUID
