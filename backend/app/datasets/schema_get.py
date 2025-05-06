from typing import Annotated, Optional
from uuid import UUID

from annotated_types import MinLen

from app.data_outputs.schema_basic import DataOutputBasic
from app.data_outputs_datasets.schema_basic import DataOutputDatasetAssociationBasic
from app.data_product_lifecycles.schema_basic import DataProductLifeCycleBasic
from app.data_product_settings.schema_basic import DataProductSettingValueBasic
from app.data_products.schema_basic import DataProductBasic
from app.data_products_datasets.schema_basic import DataProductDatasetAssociationBasic
from app.datasets.enums import DatasetAccessType
from app.datasets.status import DatasetStatus
from app.domains.schema_basic import DomainBasic
from app.shared.schema import ORMModel
from app.tags.schema_basic import TagBasic
from app.users.schema_basic import UserBasic


class DataProductLink(DataProductDatasetAssociationBasic):
    data_product: DataProductBasic


class DataOutput(DataOutputBasic):
    # Nested schemas
    owner: DataProductBasic


class DataOutputLink(DataOutputDatasetAssociationBasic):
    data_output: DataOutput


class BaseDatasetGet(ORMModel):
    id: UUID
    namespace: str
    name: str
    description: str
    status: DatasetStatus
    access_type: DatasetAccessType

    # Nested schemas
    tags: list[TagBasic]
    domain: DomainBasic
    lifecycle: Optional[DataProductLifeCycleBasic]
    data_product_settings: list[DataProductSettingValueBasic]
    data_output_links: list[DataOutputLink]
    owners: Annotated[list[UserBasic], MinLen(1)]


class DatasetGet(BaseDatasetGet):
    about: Optional[str]

    # Nested schemas
    data_product_links: list[DataProductLink]
    rolled_up_tags: set[TagBasic]


class DatasetsGet(BaseDatasetGet):
    data_product_count: int
