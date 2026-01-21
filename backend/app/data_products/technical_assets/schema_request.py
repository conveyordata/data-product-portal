from uuid import UUID
from warnings import deprecated

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
    technical_mapping: TechnicalMapping
    tag_ids: list[UUID]


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
