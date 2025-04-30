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
from app.datasets.schema import Dataset
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
    status: DataProductStatus

    # Nested schemas
    tags: list[Tag]
    lifecycle: Optional[DataProductLifeCycleBasic]
    type: DataProductTypeBasic
    domain: Domain
    data_product_settings: list[DataProductSettingValueBasic]


class MembershipLinks(DataProductMembershipBasic):
    # Nested schemas
    user: User


class DataOutputLinks(DataOutputBasic):
    # Nested schemas
    dataset_links: list[DataOutputDatasetAssociationBasic]


class DatasetLinks(DataProductDatasetAssociationBasic):
    # Nested schemas
    dataset: Dataset


class DataProductGet(BaseDataProductGet):
    # Nested schemas
    dataset_links: list[DatasetLinks]
    memberships: list[MembershipLinks]
    data_outputs: list[DataOutputLinks]
    rolled_up_tags: set[Tag]


class DataProductsGet(BaseDataProductGet):
    user_count: int
    dataset_count: int
    data_outputs_count: int
