from uuid import UUID

from app.data_products.technical_assets.enums import TechnicalMapping
from app.data_products.technical_assets.status import TechnicalAssetStatus
from app.shared.schema import ORMModel
from app.technical_asset_configuration.schema_union import DataOutputConfiguration


class TechnicalAsset(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str
    status: TechnicalAssetStatus
    technical_mapping: TechnicalMapping
    owner_id: UUID
    platform_id: UUID
    service_id: UUID

    # Nested schemas
    configuration: DataOutputConfiguration
