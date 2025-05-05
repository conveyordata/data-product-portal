from typing import Optional
from uuid import UUID

from app.data_outputs.schema_get import DataOutputGet
from app.data_product_lifecycles.schema import DataProductLifeCycle
from app.data_product_memberships.schema_get import DataProductMembershipGet
from app.data_product_settings.schema import DataProductSettingValue
from app.data_product_types.schema import DataProductType
from app.data_products.status import DataProductStatus
from app.data_products_datasets.schema import DatasetDataProductLink
from app.domains.schema import Domain
from app.shared.schema import ORMModel
from app.tags.schema import Tag


class BaseDataProductGet(ORMModel):
    id: UUID
    name: str
    description: str
    about: Optional[str]
    namespace: str
    tags: list[Tag]
    status: DataProductStatus
    lifecycle: Optional[DataProductLifeCycle]
    type: DataProductType
    domain: Domain
    data_product_settings: list[DataProductSettingValue]


class DataProductGet(BaseDataProductGet):
    dataset_links: list[DatasetDataProductLink]
    memberships: list[DataProductMembershipGet]
    data_outputs: list[DataOutputGet]
    rolled_up_tags: set[Tag]


class DataProductsGet(BaseDataProductGet):
    user_count: int
    dataset_count: int
    data_outputs_count: int
