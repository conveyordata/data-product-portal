from uuid import UUID

from app.data_output_configuration.schema_union import DataOutputConfiguration
from app.data_outputs.status import DataOutputStatus
from app.shared.schema import ORMModel


class DataOutputCreate(ORMModel):
    name: str
    description: str
    namespace: str
    platform_id: UUID
    service_id: UUID
    status: DataOutputStatus
    configuration: DataOutputConfiguration
    sourceAligned: bool
    tag_ids: list[UUID]


class DataOutputUpdate(ORMModel):
    name: str
    description: str
    tag_ids: list[UUID]


class DataOutputStatusUpdate(ORMModel):
    status: DataOutputStatus
