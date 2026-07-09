from typing import Optional, Sequence
from uuid import UUID

from pydantic import Field

from app.access_durations.enums import AccessDurationType
from app.configuration.data_product_lifecycles.schema import DataProductLifeCycle
from app.configuration.data_product_settings.schema import (
    OutputPortSettingValue,
)
from app.configuration.domains.schema import Domain
from app.configuration.tags.schema import Tag
from app.data_products.output_port_technical_assets_link.schema import (
    TechnicalAssetOutputPortAssociation,
)
from app.data_products.output_ports.data_quality.enums import DataQualityStatus
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.schema import OutputPort
from app.data_products.output_ports.status import OutputPortStatus
from app.data_products.technical_assets.schema import TechnicalAsset
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

    # Nested schemas
    tags: list[Tag]
    domain: Domain
    lifecycle: Optional[DataProductLifeCycle]


class GetOutputPortResponse(BaseOutputPortGet):
    about: Optional[str]

    rolled_up_tags: set[Tag]
    data_product_settings: list[OutputPortSettingValue]
    technical_asset_links: list[TechnicalAssetLink] = Field(
        validation_alias="data_output_links"
    )


class OutputPortsGet(BaseOutputPortGet):
    abstract_data_product_count: int
    technical_assets_count: int
    data_product_name: str
    quality_status: Optional[DataQualityStatus]


class GetDataProductOutputPortsResponse(ORMModel):
    output_ports: Sequence[OutputPort]


class CreateOutputPortResponse(ORMModel):
    id: UUID


class UpdateOutputPortResponse(ORMModel):
    id: UUID
