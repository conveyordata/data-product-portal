from uuid import UUID

from app.shared.schema import ORMModel
from app.technical_asset_configuration.schema_union import DataOutputConfiguration


class RenderTechnicalAssetAccessPathRequest(ORMModel):
    platform_id: UUID
    service_id: UUID
    configuration: DataOutputConfiguration
