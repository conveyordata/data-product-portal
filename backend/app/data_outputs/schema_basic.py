from uuid import UUID

from app.data_output_configuration.schema_union import DataOutputConfiguration
from app.data_outputs.status import DataOutputStatus
from app.data_products.schema_base_get import BaseDataProductGet
from app.shared.schema import ORMModel


class DataOutputBasic(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str
    status: DataOutputStatus
    sourceAligned: bool
    owner_id: UUID
    platform_id: UUID
    service_id: UUID

    # Nested schemas
    configuration: DataOutputConfiguration
    owner: BaseDataProductGet
