from uuid import UUID

from pydantic import Field

from app.data_outputs.schema_union import DataOutputConfiguration
from app.data_outputs.status import DataOutputStatus
from app.data_products.schema_base_get import BaseDataProductGet
from app.shared.schema import ORMModel


class DataOutputBaseGet(ORMModel):
    owner_id: UUID = Field(
        ..., descrpition="Id of the data product that owns the data output"
    )
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
    owner: BaseDataProductGet = Field(
        ..., description="Data product who owns the data output"
    )
    status: DataOutputStatus = Field(
        ..., description="Current status of the data output"
    )
    configuration: DataOutputConfiguration = Field(
        ..., description="Configuration settings for the data output"
    )
