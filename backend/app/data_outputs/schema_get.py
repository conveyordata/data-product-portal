from uuid import UUID

from app.data_output_configuration.schema_union import DataOutputConfiguration
from app.data_outputs.status import DataOutputStatus
from app.data_outputs_datasets.schema_basic import DataOutputDatasetAssociationBasic
from app.data_products.schema_base_get import BaseDataProductGet
from app.datasets.schema import Dataset
from app.shared.schema import ORMModel
from app.tags.schema import Tag


class BaseDataOutputGet(ORMModel):
    id: UUID
    name: str
    description: str
    namespace: str
    owner_id: UUID
    platform_id: UUID
    service_id: UUID
    status: DataOutputStatus

    # Nested schemas
    configuration: DataOutputConfiguration
    owner: BaseDataProductGet


class DatasetLink(DataOutputDatasetAssociationBasic):
    # Nested schemas
    dataset: Dataset


class DataOutputGet(BaseDataOutputGet):
    # Nested schemas
    dataset_links: list[DatasetLink]
    tags: list[Tag]


class DataOutputsGet(BaseDataOutputGet):
    pass
