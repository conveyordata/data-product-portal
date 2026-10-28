from uuid import UUID

from app.data_products.technical_assets.enums import TechnicalMapping
from app.shared.schema import ORMModel
from app.technical_asset_configuration.schema_union import DataOutputConfiguration


class RenderTechnicalAssetAccessPathRequest(ORMModel):
    platform_id: UUID
    service_id: UUID
    data_product_id: UUID
    namespace: str
    technical_mapping: TechnicalMapping
    configuration: DataOutputConfiguration
