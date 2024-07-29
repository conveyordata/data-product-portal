from uuid import UUID

from app.data_outputs.data_output_types import DataOutputTypes
from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.datasets.schema import Dataset
from app.shared.schema import ORMModel


class DatasetLink(DataOutputDatasetAssociation):
    dataset: Dataset


class DataOutputGet(ORMModel):
    id: UUID
    name: str
    description: str
    external_id: str
    owner_id: UUID
    configuration_type: DataOutputTypes
    dataset_links: list[DatasetLink]
