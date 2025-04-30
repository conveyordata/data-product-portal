from typing import Optional
from uuid import UUID

from app.data_outputs.schema_get import DataOutputGet
from app.data_product_lifecycles.schema_basic import DataProductLifeCycleBasic
from app.data_product_memberships.schema_basic import DataProductMembershipBasic
from app.data_product_settings.schema_basic import DataProductSettingValueBasic
from app.data_product_types.schema_basic import DataProductTypeBasic
from app.data_products.status import DataProductStatus
from app.data_products_datasets.schema import DatasetDataProductLink
from app.domains.schema import Domain
from app.shared.schema import ORMModel
from app.tags.schema import Tag
from app.users.schema import User


class BaseDataProductGet(ORMModel):
    id: UUID
    name: str
    description: str
    about: Optional[str]
    namespace: str
    tags: list[Tag]
    status: DataProductStatus
    lifecycle: Optional[DataProductLifeCycleBasic]
    type: DataProductTypeBasic
    domain: Domain
    data_product_settings: list[DataProductSettingValueBasic]


class MembershipLinks(DataProductMembershipBasic):
    user: User


class DataProductGet(BaseDataProductGet):
    dataset_links: list[DatasetDataProductLink]
    memberships: list[MembershipLinks]
    data_outputs: list[DataOutputGet]
    rolled_up_tags: set[Tag]


class DataProductsGet(BaseDataProductGet):
    user_count: int
    dataset_count: int
    data_outputs_count: int
