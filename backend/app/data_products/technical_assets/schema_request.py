from uuid import UUID
from warnings import deprecated, warn

from pydantic import Field, model_validator

from app.data_output_configuration.schema_union import DataOutputConfiguration
from app.data_products.technical_assets.enums import TechnicalMapping
from app.data_products.technical_assets.status import TechnicalAssetStatus
from app.shared.schema import ORMModel


class CreateTechnicalAssetRequest(ORMModel):
    name: str
    description: str
    namespace: str
    platform_id: UUID
    service_id: UUID
    status: TechnicalAssetStatus
    configuration: DataOutputConfiguration
    sourceAligned: bool | None = Field(
        default=None,
        deprecated=True,
        description="DEPRECATED: Use 'technical_mapping' instead. "
        "This field will be removed in a future version.",
    )
    technical_mapping: TechnicalMapping | None = Field(
        default=None,
    )
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
                # Convert sourceAligned to technical_mapping
                self.technical_mapping = (
                    TechnicalMapping.Custom
                    if self.sourceAligned
                    else TechnicalMapping.Default
                )
            # If both are provided, technical_mapping takes precedence (already set)

        # If neither was provided, default to Default
        if self.technical_mapping is None:
            self.technical_mapping = TechnicalMapping.Default

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
