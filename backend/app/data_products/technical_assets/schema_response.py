from typing import Any, Optional, Sequence
from uuid import UUID

from pydantic import Field, computed_field
from sdk.plugins.context import PluginContext

from app.configuration.access_modes.schema_response import AccessMode
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
from app.plugins.loader import discover_plugins
from app.plugins.runtime import call_plugin
from app.shared.schema import ORMModel
from app.technical_asset_configuration.schema_union import DataOutputConfiguration


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


class OutputPortLink(TechnicalAssetOutputPortAssociation):
    output_port: OutputPort


class GetTechnicalAssetsResponseItem(ORMModel):
    id: UUID
    name: str
    description: str
    namespace: str
    owner_id: UUID
    platform_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    status: TechnicalAssetStatus
    technical_mapping: TechnicalMapping
    access_modes: list[AccessMode]

    # Exactly one of `configuration` (a built-in type) or `plugin_key` (a
    # dynamically loaded plugin, ADR-0024) is set. `values` is the plugin's
    # own configured field values - not populated by `model_validate` (the
    # plugin's row lives in its own table, outside the portal's ORM graph),
    # hydrated afterwards by `TechnicalAssetService.hydrate_plugin_values`.
    configuration: Optional[DataOutputConfiguration] = None
    plugin_key: Optional[str] = None
    values: Optional[dict[str, Any]] = None
    owner: DataProduct

    service: Optional[PlatformService] = Field(default=None, exclude=True)
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
        if self.plugin_key:
            return self._render_plugin_result()
        configuration, service = self._require_built_in_configuration()
        return configuration.render_template(service.result_string_template)

    @computed_field
    def technical_info(self) -> list[TechnicalInfo]:
        if self.plugin_key:
            # A dynamically loaded plugin that ignores the platform/environment
            # layer (the ADR's default) has no per-environment info to report.
            return []
        configuration, service = self._require_built_in_configuration()
        return compute_technical_info(
            configuration, service, self.environment_configurations
        )

    def _require_built_in_configuration(
        self,
    ) -> tuple[DataOutputConfiguration, PlatformService]:
        # A row backed by a built-in type always has configuration/service set -
        # they're only Optional to also allow a plugin-backed row's shape.
        if self.configuration is None or self.service is None:
            raise ValueError(
                f"Technical asset {self.id} has neither `configuration` nor "
                "`plugin_key` set - not a valid row."
            )
        return self.configuration, self.service

    def _render_plugin_result(self) -> str:
        plugin_cls = next(
            (p for p in discover_plugins() if p.key == self.plugin_key), None
        )
        if not plugin_cls:
            return ""
        context = PluginContext(
            technical_asset_id=self.id,
            technical_asset_name=self.name,
            data_product_id=self.owner_id,
        )
        result = call_plugin(
            plugin_cls.key,
            "render_result",
            plugin_cls.render_result,
            self.values or {},
            context,
        )
        return result.value if result.ok else (result.error or "")

    output_port_links: list[OutputPortLink] = Field(validation_alias="dataset_links")
    tags: list[Tag]


class GetTechnicalAssetsResponse(ORMModel):
    technical_assets: Sequence[GetTechnicalAssetsResponseItem]


class UpdateTechnicalAssetResponse(ORMModel):
    id: UUID


class CreateTechnicalAssetResponse(ORMModel):
    id: UUID
