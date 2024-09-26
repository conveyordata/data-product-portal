import json
from uuid import UUID

from pydantic import field_validator

from app.data_outputs.schema_get import DatasetLink
from app.data_outputs.schema_union import DataOutputs, DataOutputTypes
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
    configuration: DataOutputs
    sourceAligned: bool


class DataOutputUpdate(ORMModel):
    name: str
    description: str
    # configuration: DataOutputs


class DataOutputRegister(ORMModel):
    name: str
    description: str
    external_id: str
    configuration: DataOutputs


class DataOutput(ORMModel):
    id: UUID
    name: str
    description: str
    external_id: str
    platform_id: UUID
    service_id: UUID
    owner: BaseDataProductGet
    status: DataOutputStatus
    configuration: DataOutputs
    configuration_type: DataOutputTypes
    dataset_links: list[DatasetLink]

    @field_validator("configuration", mode="before")
    @classmethod
    def parse_settings(cls, v: str | dict) -> dict:
        if isinstance(v, str):
            return json.loads(v)
        return v


class DataOutputToDB(ORMModel):
    name: str
    description: str
    external_id: str
    owner_id: UUID
    platform_id: UUID
    service_id: UUID
    configuration: str
    status: DataOutputStatus
    configuration_type: DataOutputTypes