from uuid import UUID

from app.data_output_configuration.schema_union import DataOutputConfiguration
from app.shared.schema import ORMModel


class RenderTechnicalAssetAccessPathRequest(ORMModel):
    platform_id: UUID
    service_id: UUID
    configuration: DataOutputConfiguration
