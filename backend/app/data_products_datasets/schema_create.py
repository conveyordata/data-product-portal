from uuid import UUID

from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetModel,
)
from app.shared.schema import ORMModel


class DataProductDatasetAssociationCreate(ORMModel):
    dataset_id: UUID
    status: DataProductDatasetLinkStatus = DataProductDatasetLinkStatus.PENDING_APPROVAL

    class Meta:
        orm_model = DataProductDatasetModel


class DataProductDatasetAssociationUpdate(DataProductDatasetAssociationCreate):
    pass
