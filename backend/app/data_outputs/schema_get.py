from app.data_outputs.schema_base_get import DataOutputBaseGet
from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.datasets.schema import Dataset


class DatasetLink(DataOutputDatasetAssociation):
    dataset: Dataset


class DataOutputGet(DataOutputBaseGet):
    dataset_links: list[DatasetLink]
