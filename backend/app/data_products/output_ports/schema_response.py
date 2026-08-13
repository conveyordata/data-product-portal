from typing import Optional, Sequence
from uuid import UUID

from pydantic import AliasPath, ConfigDict, Field

from app.configuration.access_durations.enums import AccessDurationType
from app.configuration.access_modes.schema_response import AccessMode
from app.configuration.data_product_lifecycles.schema import DataProductLifeCycle
from app.configuration.data_product_settings.schema import (
    OutputPortSettingValue,
)
from app.configuration.domains.schema import Domain
from app.configuration.tags.schema import Tag
from app.data_products.output_port_technical_assets_link.schema import (
    TechnicalAssetOutputPortAssociation,
)
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.schema import OutputPort
from app.data_products.output_ports.status import OutputPortStatus
from app.data_products.technical_assets.schema import (
    TechnicalAsset,
)
from app.shared.schema import ORMModel


class TechnicalAssetLink(TechnicalAssetOutputPortAssociation):
    technical_asset: TechnicalAsset = Field(validation_alias="data_output")


class OutputPortAccessDuration(ORMModel):
    access_duration_type: AccessDurationType
    days: int


class GetOutputPortAccessDurationsResponse(ORMModel):
    id: UUID
    data_product_access_duration: OutputPortAccessDuration
    exploration_access_duration: OutputPortAccessDuration


class BaseOutputPortGet(ORMModel):
    model_config = ConfigDict(
        from_attributes=True, validate_by_name=True, validate_by_alias=True
    )

    id: UUID
    namespace: str
    name: str
    description: str
    status: OutputPortStatus
    usage: Optional[str]
    access_type: OutputPortAccessType
    data_product_access_duration_type: AccessDurationType
    exploration_access_duration_type: AccessDurationType
    data_product_id: UUID

    tags: list[Tag]
    domain: Domain = Field(validation_alias=AliasPath("data_product", "domain"))
    lifecycle: Optional[DataProductLifeCycle]
    access_modes: list[AccessMode]


class GetOutputPortResponse(BaseOutputPortGet):
    about: Optional[str]

    rolled_up_tags: set[Tag]
    data_product_settings: list[OutputPortSettingValue]
    technical_asset_links: list[TechnicalAssetLink] = Field(
        validation_alias="data_output_links"
    )


class GetDataProductOutputPortsResponse(ORMModel):
    output_ports: Sequence[OutputPort]


class CreateOutputPortResponse(ORMModel):
    id: UUID


class UpdateOutputPortResponse(ORMModel):
    id: UUID
