from typing import Annotated, Optional
from uuid import UUID

from annotated_types import MinLen

from app.data_outputs.schema import DataOutput as DataOutputBaseSchema
from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.data_product_lifecycles.schema import DataProductLifeCycle
from app.data_product_settings.schema import DataProductSettingValue
from app.data_products.schema import DataProduct
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.datasets.enums import DatasetAccessType
from app.datasets.status import DatasetStatus
from app.domains.schema import Domain
from app.shared.schema import ORMModel
from app.tags.schema import Tag
from app.users.schema import User


class DataProductLink(DataProductDatasetAssociation):
    data_product: DataProduct


class DataOutput(DataOutputBaseSchema):
    # Nested schemas
    owner: DataProduct


class DataOutputLink(DataOutputDatasetAssociation):
    data_output: DataOutput


class BaseDatasetGet(ORMModel):
    id: UUID
    namespace: str
    name: str
    description: str
    status: DatasetStatus
    access_type: DatasetAccessType

    # Nested schemas
    tags: list[Tag]
    domain: Domain
    lifecycle: Optional[DataProductLifeCycle]
    data_product_settings: list[DataProductSettingValue]
    data_output_links: list[DataOutputLink]
    owners: Annotated[list[User], MinLen(1)]


class DatasetGet(BaseDatasetGet):
    about: Optional[str]

    # Nested schemas
    data_product_links: list[DataProductLink]
    rolled_up_tags: set[Tag]


class DatasetsGet(BaseDatasetGet):
    data_product_count: int
