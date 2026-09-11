from typing import Any, Optional
from uuid import UUID
from warnings import deprecated, warn

from pydantic import Field, model_validator

from app.data_products.technical_assets.enums import TechnicalMapping
from app.data_products.technical_assets.status import TechnicalAssetStatus
from app.shared.schema import ORMModel
from app.technical_asset_configuration.schema_union import DataOutputConfiguration


class CreateTechnicalAssetRequest(ORMModel):
    name: str
    description: str
    namespace: str
    # Exactly one of (platform_id, service_id, configuration) - a built-in type -
    # or (plugin_key, values) - a dynamically loaded plugin (ADR-0024) - must be
    # given. See `validate_configuration_shape` below.
    platform_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    configuration: Optional[DataOutputConfiguration] = None
    plugin_key: Optional[str] = None
    values: Optional[dict[str, Any]] = None
    sourceAligned: bool | None = Field(
        default=None,
        deprecated=True,
        description="DEPRECATED: Use 'technical_mapping' instead. "
        "This field will be removed in a future version.",
    )
    technical_mapping: TechnicalMapping | None = Field(
        default=None,
    )
    access_mode_ids: list[UUID] = Field(default=[])
    tag_ids: list[UUID]

    @model_validator(mode="after")
    def handle_deprecated_sourceAligned(self):
        """
        Handle backwards compatibility for deprecated sourceAligned field.

        - If only sourceAligned is provided: convert to technical_mapping
        - If only technical_mapping is provided: use it
        - If both are provided: technical_mapping takes precedence, warn user
        - If neither is provided: default to TechnicalMapping.Default
        """
        if self.sourceAligned is not None:
            warn(
                "The 'sourceAligned' field is deprecated and will be removed in a future version. "
                "Please use 'technical_mapping' instead.",
                DeprecationWarning,
                stacklevel=2,
            )

            if self.technical_mapping is None:
                self.technical_mapping = (
                    TechnicalMapping.Custom
                    if self.sourceAligned
                    else TechnicalMapping.Default
                )

        if self.technical_mapping is None:
            self.technical_mapping = TechnicalMapping.Default

        return self

    @model_validator(mode="after")
    def validate_configuration_shape(self):
        is_plugin_backed = self.plugin_key is not None
        if is_plugin_backed == (self.configuration is not None):
            raise ValueError(
                "Provide exactly one of `configuration` (a built-in type) or "
                "`plugin_key` (a dynamically loaded plugin)."
            )
        if is_plugin_backed:
            if self.values is None:
                self.values = {}
        elif self.platform_id is None or self.service_id is None:
            raise ValueError(
                "platform_id and service_id are required when configuration is provided."
            )
        return self


@deprecated("Use CreateTechnicalAssetRequest instead")
class DataOutputCreate(CreateTechnicalAssetRequest):
    pass


class DataOutputUpdate(ORMModel):
    name: str
    description: str
    tag_ids: list[UUID]


class DataOutputStatusUpdate(ORMModel):
    status: TechnicalAssetStatus


class DataOutputResultStringRequest(ORMModel):
    platform_id: UUID
    service_id: UUID
    configuration: DataOutputConfiguration
