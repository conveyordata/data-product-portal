import json
from uuid import UUID

from pydantic import field_validator

from app.data_outputs.schema_union import DataOutputs, DataOutputTypes
from app.data_outputs.status import DataOutputStatus
from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.data_products.schema import DataProduct
from app.shared.schema import ORMModel


class DataOutputCreate(ORMModel):
    name: str
    description: str
    external_id: str
    owner_id: UUID
    status: DataOutputStatus
    configuration: DataOutputs


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
    owner: DataProduct
    status: DataOutputStatus
    configuration: DataOutputs
    configuration_type: DataOutputTypes
    dataset_links: list[DataOutputDatasetAssociation]

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
    configuration: str
    status: DataOutputStatus
    configuration_type: DataOutputTypes
