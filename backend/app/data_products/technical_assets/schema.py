from typing import Optional
from uuid import UUID
from warnings import deprecated

from app.data_output_configuration.schema_union import DataOutputConfiguration
from app.data_products.technical_assets.status import TechnicalAssetStatus
from app.shared.schema import ORMModel


class TechnicalAsset(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str
    status: TechnicalAssetStatus
    sourceAligned: Optional[bool]
    owner_id: UUID
    platform_id: UUID
    service_id: UUID

    # Nested schemas
    configuration: DataOutputConfiguration


@deprecated("Use TechnicalAsset instead")
class DataOutput(TechnicalAsset):
    def convert(self):
        return TechnicalAsset(**self.model_dump())
