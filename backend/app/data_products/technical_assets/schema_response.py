from typing import Any, Optional, Sequence
from uuid import UUID

from pydantic import AliasPath, Field, computed_field

from app.configuration.access_modes.schema_response import AccessMode
from app.configuration.domains.schema import Domain
from app.configuration.environments.schema_response import Environment
from app.configuration.tags.schema import Tag
from app.data_products.output_port_technical_assets_link.schema import (
    TechnicalAssetOutputPortAssociation,
)
from app.data_products.output_ports.schema import OutputPort
from app.data_products.schema import DataProduct
from app.data_products.schema_response import DataProductEnvironment
from app.data_products.technical_assets.enums import TechnicalMapping
from app.data_products.technical_assets.status import TechnicalAssetStatus
from app.shared.schema import ORMModel
from app.technical_asset_configuration.base_schema import (
    PluginContext,
    TechnicalAssetContext,
)
from app.technical_asset_configuration.schema_union import DataOutputConfiguration


class TechnicalInfo(ORMModel):
    environment_id: UUID
    environment: str
    info: Optional[str]


class PlatformSettingsForEnvironment(ORMModel):
    environment: Environment
    settings: dict[str, Any]


def compute_technical_info(
    configuration: DataOutputConfiguration,
    platform_settings: list[PlatformSettingsForEnvironment],
    plugin_context: PluginContext,
) -> list[TechnicalInfo]:
    metadata = configuration.get_platform_metadata()
    if metadata.result_string_template is None:
        return []
    template = metadata.technical_info_template or metadata.result_string_template
    result = []
    for item in platform_settings:
        settings = configuration.platform.settings_model.model_validate(item.settings)
        plugin_config = configuration.get_configuration(
            getattr(settings, configuration.settings_field(), [])
        )
        context = plugin_config.model_dump() if plugin_config else {}
        context["environment"] = item.environment.acronym
        info = configuration.render_template(
            template, plugin_context=plugin_context, **context
        )
        result.append(
            TechnicalInfo(
                environment_id=item.environment.id,
                environment=item.environment.name,
                info=info,
            )
        )
    return result


class OutputPortLink(TechnicalAssetOutputPortAssociation):
    output_port: OutputPort


class GetTechnicalAssetsResponseItem(ORMModel):
    id: UUID
    name: str
    description: str
    namespace: str
    owner_id: UUID
    status: TechnicalAssetStatus
    technical_mapping: TechnicalMapping
    access_modes: list[AccessMode]

    configuration: DataOutputConfiguration
    owner: DataProduct
    environments: list[DataProductEnvironment] = Field(
        validation_alias=AliasPath("owner", "environments")
    )

    platform_settings: list[PlatformSettingsForEnvironment] = Field(
        default=[], exclude=True
    )
    domain: Domain = Field(validation_alias=AliasPath("owner", "domain"), exclude=True)

    def plugin_context(self) -> PluginContext:
        return PluginContext(
            technical_asset=TechnicalAssetContext.model_validate(self),
            data_product=self.owner,
            domain=self.domain,
        )

    @computed_field(
        description="DEPRECATED: Use 'technical_mapping' instead. "
        "This field will be removed in a future version."
    )
    def sourceAligned(self) -> bool:
        """Backwards compatibility: convert technical_mapping back to source_aligned."""
        return self.technical_mapping == TechnicalMapping.Custom

    @computed_field
    def result_string(self) -> str:
        template = self.configuration.get_platform_metadata().result_string_template
        if template is None:
            return ""
        return self.configuration.render_template(
            template, plugin_context=self.plugin_context()
        )

    @computed_field
    def technical_info(self) -> list[TechnicalInfo]:
        return compute_technical_info(
            self.configuration, self.platform_settings, self.plugin_context()
        )

    output_port_links: list[OutputPortLink]
    tags: list[Tag]


class GetTechnicalAssetsResponse(ORMModel):
    technical_assets: Sequence[GetTechnicalAssetsResponseItem]


class UpdateTechnicalAssetResponse(ORMModel):
    id: UUID


class CreateTechnicalAssetResponse(ORMModel):
    id: UUID
