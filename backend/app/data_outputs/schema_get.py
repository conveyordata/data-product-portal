from uuid import UUID

from app.data_outputs.schema_union import DataOutputConfiguration
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
    configuration: DataOutputConfiguration
    status: DataOutputStatus
    dataset_links: list[DatasetLink]
