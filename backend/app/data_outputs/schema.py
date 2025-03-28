from uuid import UUID

from app.data_outputs.schema_get import DatasetLink
from app.data_outputs.schema_union import DataOutputConfiguration
from app.data_outputs.status import DataOutputStatus
from app.data_products.schema_base_get import BaseDataProductGet
from app.shared.schema import ORMModel
from app.tags.schema import Tag


class DataOutputCreateRequest(ORMModel):
    name: str
    description: str
    external_id: str

    platform_id: UUID
    service_id: UUID
    status: DataOutputStatus
    configuration: DataOutputConfiguration
    sourceAligned: bool
    tag_ids: list[UUID]


class DataOutputCreate(DataOutputCreateRequest):
    owner_id: UUID


class DataOutputUpdate(ORMModel):
    name: str
    description: str
    tag_ids: list[UUID]


class DataOutputStatusUpdate(ORMModel):
    status: DataOutputStatus


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
    tags: list[Tag]
