from typing import Annotated, Optional
from uuid import UUID

from annotated_types import MinLen

from app.data_outputs.schema_basic import DataOutputBasic
from app.data_outputs_datasets.schema_basic import DataOutputDatasetAssociationBasic
from app.data_product_lifecycles.schema import DataProductLifeCycle
from app.data_product_settings.schema import DataProductSettingValue
from app.data_products.schema_base_get import BaseDataProductGet
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.datasets.enums import DatasetAccessType
from app.datasets.status import DatasetStatus
from app.domains.schema import Domain
from app.shared.schema import ORMModel
from app.tags.schema import Tag
from app.users.schema import User


class DataProductLink(DataProductDatasetAssociation):
    data_product: BaseDataProductGet


class DataOutputLink(DataOutputDatasetAssociationBasic):
    data_output: DataOutputBasic


class BaseDatasetGet(ORMModel):
    id: UUID
    namespace: str
    name: str
    description: str
    owners: Annotated[list[User], MinLen(1)]
    lifecycle: Optional[DataProductLifeCycle]
    status: DatasetStatus
    tags: list[Tag]
    domain: Domain
    access_type: DatasetAccessType
    data_output_links: list[DataOutputLink]
    data_product_settings: list[DataProductSettingValue]


class DatasetGet(BaseDatasetGet):
    about: Optional[str] = None
    data_product_links: list[DataProductLink]
    rolled_up_tags: set[Tag]


class DatasetsGet(BaseDatasetGet):
    data_product_count: int
