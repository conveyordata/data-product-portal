from typing import Optional, Sequence
from uuid import UUID

from pydantic import Field, computed_field

from app.configuration.environments.platform_service_configurations.schema_response import (
    EnvironmentConfigsGetItem,
)
from app.configuration.platforms.platform_services.schema import PlatformService
from app.configuration.tags.schema import Tag
from app.data_output_configuration.schema_union import DataOutputConfiguration
from app.data_products.output_port_technical_assets_link.schema import (
    TechnicalAssetOutputPortAssociation,
)
from app.data_products.output_ports.schema import OutputPort
from app.data_products.schema import DataProduct
from app.data_products.technical_assets.enums import TechnicalMapping
from app.data_products.technical_assets.status import TechnicalAssetStatus
from app.shared.schema import ORMModel


class TechnicalInfo(ORMModel):
    environment_id: UUID
    environment: str
    info: Optional[str]


def compute_technical_info(
    configuration: DataOutputConfiguration,
    service: PlatformService,
    environment_configurations: list[EnvironmentConfigsGetItem],
) -> list[TechnicalInfo]:
    result = []
    for env_config in environment_configurations:
        plugin_config = configuration.get_configuration(env_config.config)
        context = plugin_config.model_dump() if plugin_config else {}
        context["environment"] = env_config.environment.acronym
        info = configuration.render_template(service.technical_info_template, **context)
        result.append(
            TechnicalInfo(
                environment_id=env_config.environment.id,
                environment=env_config.environment.name,
                info=info,
            )
        )
    return result


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

    # Nested schemas
    configuration: DataOutputConfiguration
    owner: DataProduct

    # Excluded
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
        return compute_technical_info(
            self.configuration, self.service, self.environment_configurations
        )


class OutputPortLink(TechnicalAssetOutputPortAssociation):
    output_port: OutputPort = Field(validation_alias="dataset")


class GetTechnicalAssetsResponseItem(BaseTechnicalAssetGet):
    # Nested schemas
    output_port_links: list[OutputPortLink] = Field(validation_alias="dataset_links")
    tags: list[Tag]


class GetTechnicalAssetsResponse(ORMModel):
    technical_assets: Sequence[GetTechnicalAssetsResponseItem]


class UpdateTechnicalAssetResponse(ORMModel):
    id: UUID


class CreateTechnicalAssetResponse(ORMModel):
    id: UUID
