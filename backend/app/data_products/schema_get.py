from typing import Optional
from uuid import UUID

from app.data_outputs.schema_basic import DataOutputBasic
from app.data_outputs_datasets.schema_basic import DataOutputDatasetAssociationBasic
from app.data_product_lifecycles.schema_basic import DataProductLifeCycleBasic
from app.data_product_memberships.schema_basic import DataProductMembershipBasic
from app.data_product_settings.schema_basic import DataProductSettingValueBasic
from app.data_product_types.schema_basic import DataProductTypeBasic
from app.data_products.status import DataProductStatus
from app.data_products_datasets.schema_basic import DataProductDatasetAssociationBasic
from app.datasets.schema_basic import DatasetBasic
from app.domains.schema_basic import DomainBasic
from app.shared.schema import ORMModel
from app.tags.schema_basic import TagBasic
from app.users.schema_basic import UserBasic


class BaseDataProductGet(ORMModel):
    id: UUID
    name: str
    description: str
    namespace: str
    status: DataProductStatus

    # Nested schemas
    tags: list[TagBasic]
    domain: DomainBasic
    type: DataProductTypeBasic
    lifecycle: Optional[DataProductLifeCycleBasic]
    data_product_settings: list[DataProductSettingValueBasic]


class MembershipLinks(DataProductMembershipBasic):
    # Nested schemas
    user: UserBasic


class DataOutputLinks(DataOutputBasic):
    # Nested schemas
    dataset_links: list[DataOutputDatasetAssociationBasic]


class DatasetLinks(DataProductDatasetAssociationBasic):
    # Nested schemas
    dataset: DatasetBasic


class DataProductGet(BaseDataProductGet):
    about: Optional[str]

    # Nested schemas
    dataset_links: list[DatasetLinks]
    memberships: list[MembershipLinks]
    data_outputs: list[DataOutputLinks]
    rolled_up_tags: set[TagBasic]


class DataProductsGet(BaseDataProductGet):
    user_count: int
    dataset_count: int
    data_outputs_count: int
