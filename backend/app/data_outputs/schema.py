from uuid import UUID

from app.data_outputs.schema_get import DatasetLink
from app.data_outputs.schema_union import DataOutputConfiguration
from app.data_outputs.status import DataOutputStatus
from app.data_products.schema_base_get import BaseDataProductGet
from app.shared.schema import ORMModel


class DataOutputCreate(ORMModel):
    name: str
    description: str
    external_id: str
    owner_id: UUID
    platform_id: UUID
    service_id: UUID
    status: DataOutputStatus
    configuration: DataOutputConfiguration
    sourceAligned: bool


class DataOutputUpdate(ORMModel):
    name: str
    description: str


class DataOutput(ORMModel):
    id: UUID
    name: str
    description: str
    external_id: str
    platform_id: UUID
    service_id: UUID
    owner: BaseDataProductGet
    status: DataOutputStatus
    configuration: DataOutputConfiguration
    dataset_links: list[DatasetLink]
