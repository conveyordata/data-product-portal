from pydantic import Field

from app.data_outputs.schema_base_get import DataOutputBaseGet
from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.datasets.schema import Dataset
from app.tags.schema import Tag


class DatasetLink(DataOutputDatasetAssociation):
    dataset: Dataset = Field(
        ..., description="The dataset used in the link between dataset and data output"
    )


class DataOutputGet(DataOutputBaseGet):
    dataset_links: list[DatasetLink] = Field(
        ..., description="Links to datasets associated with the data output"
    )
    tags: list[Tag] = Field(
        ..., description="List of tags associated with the data output"
    )
