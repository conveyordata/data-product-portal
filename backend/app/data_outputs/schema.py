from uuid import UUID

from pydantic import Field

from app.data_outputs.schema_get import DatasetLink
from app.data_outputs.schema_union import DataOutputConfiguration
from app.data_outputs.status import DataOutputStatus
from app.data_products.schema_base_get import BaseDataProductGet
from app.shared.schema import ORMModel
from app.tags.schema import Tag


class DataOutputCreate(ORMModel):
    name: str = Field(..., description="Name of the data output")
    description: str = Field(..., description="Description of the data output")
    external_id: str = Field(..., description="External identifier for the data output")
    owner_id: UUID = Field(
        ..., description="Unique identifier of the owner of the data output"
    )
    platform_id: UUID = Field(
        ...,
        description="Unique identifier of the platform associated with the data output",
    )
    service_id: UUID = Field(
        ...,
        description="Unique identifier of the service associated with the data output",
    )
    status: DataOutputStatus = Field(
        ..., description="Current status of the data output"
    )
    configuration: DataOutputConfiguration = Field(
        ..., description="Configuration settings for the data output"
    )
    sourceAligned: bool = Field(
        ..., description="Indicates if the data output is source-aligned"
    )
    tag_ids: list[UUID] = Field(
        ..., description="List of tags associated with the data output"
    )


class DataOutputUpdate(ORMModel):
    name: str = Field(..., description="Name of the data output")
    description: str = Field(..., description="Description of the data output")
    tag_ids: list[UUID] = Field(
        ..., description="List of tags associated with the data output"
    )


class DataOutputStatusUpdate(ORMModel):
    status: DataOutputStatus = Field(
        ..., description="Current status of the data output"
    )


class DataOutput(ORMModel):
    id: UUID = Field(..., description="Unique identifier for the data output")
    name: str = Field(..., description="Name of the data output")
    description: str = Field(..., description="Description of the data output")
    external_id: str = Field(..., description="External identifier for the data output")
    platform_id: UUID = Field(
        ...,
        description="Unique identifier of the platform associated with the data output",
    )
    service_id: UUID = Field(
        ...,
        description="Unique identifier of the service associated with the data output",
    )
    owner: BaseDataProductGet = Field(..., description="Owner of the data output")
    status: DataOutputStatus = Field(
        ..., description="Current status of the data output"
    )
    configuration: DataOutputConfiguration = Field(
        ..., description="Configuration settings for the data output"
    )
    dataset_links: list[DatasetLink] = Field(
        ..., description="Links to datasets associated with the data output"
    )
    tags: list[Tag] = Field(
        ..., description="List of tags associated with the data output"
    )
