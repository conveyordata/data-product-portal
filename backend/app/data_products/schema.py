from typing import Optional
from uuid import UUID

from app.business_areas.schema import BusinessArea
from app.data_outputs.schema_get import DataOutputGet
from app.data_product_memberships.schema import (
    DataProductMembership,
    DataProductMembershipCreate,
)
from app.data_products.schema_base import BaseDataProduct
from app.data_products.status import DataProductStatus
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.shared.schema import ORMModel
from app.tags.schema import Tag


class DataProductCreate(BaseDataProduct):
    memberships: list[DataProductMembershipCreate]
    business_area_id: UUID


class DataProductUpdate(DataProductCreate):
    pass


class DataProductAboutUpdate(ORMModel):
    about: str


class DataProduct(BaseDataProduct):
    id: UUID
    status: DataProductStatus
    dataset_links: list[DataProductDatasetAssociation]
    tags: list[Tag]
    memberships: list[DataProductMembership]
    business_area: BusinessArea
    about: Optional[str] = None
    data_outputs: list[DataOutputGet]
