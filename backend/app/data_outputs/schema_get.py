import json
from uuid import UUID

from pydantic import field_validator

from app.data_outputs.schema_union import DataOutputs
from app.data_outputs.status import DataOutputStatus
from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.data_products.schema_base_get import BaseDataProductGet
from app.datasets.schema import Dataset
from app.shared.schema import ORMModel


class DatasetLink(DataOutputDatasetAssociation):
    dataset: Dataset


class DataOutputGet(ORMModel):
    id: UUID
    name: str
    description: str
    external_id: str
    owner: BaseDataProductGet
    owner_id: UUID
    platform_id: UUID
    service_id: UUID
    configuration: DataOutputs
    status: DataOutputStatus
    dataset_links: list[DatasetLink]

    @field_validator("configuration", mode="before")
    @classmethod
    def parse_settings(cls, v: str | dict) -> dict:
        if isinstance(v, str):
            return json.loads(v)
        return v
