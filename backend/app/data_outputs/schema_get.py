from app.data_outputs.schema_base_get import DataOutputBaseGet
from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.datasets.schema import Dataset
from app.tags.schema import Tag


class DatasetLink(DataOutputDatasetAssociation):
    dataset: Dataset


class DataOutputGet(DataOutputBaseGet):
    dataset_links: list[DatasetLink]
    tags: list[Tag]
