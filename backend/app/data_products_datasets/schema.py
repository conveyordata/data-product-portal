from datetime import datetime
from uuid import UUID

from app.data_products.schema_base_get import BaseDataProductGet
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetModel,
)
from app.datasets.schema import Dataset
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseDataProductDatasetAssociation(ORMModel):
    dataset_id: UUID
    status: DataProductDatasetLinkStatus = DataProductDatasetLinkStatus.PENDING_APPROVAL

    class Meta:
        orm_model = DataProductDatasetModel


class DataProductDatasetAssociationCreate(BaseDataProductDatasetAssociation):
    pass


class DataProductDatasetAssociationUpdate(BaseDataProductDatasetAssociation):
    pass


class DataProductDatasetAssociation(BaseDataProductDatasetAssociation):
    id: UUID
    data_product_id: UUID
    dataset: Dataset
    data_product: BaseDataProductGet
    status: DataProductDatasetLinkStatus
    requested_by: User
    denied_by: User | None
    approved_by: User | None
    requested_on: datetime
    denied_on: datetime | None
    approved_on: datetime | None


class DatasetDataProductLink(DataProductDatasetAssociation):
    dataset: Dataset
