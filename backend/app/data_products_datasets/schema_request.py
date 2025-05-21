from uuid import UUID

from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetModel,
)
from app.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel


class DataProductDatasetAssociationCreate(ORMModel):
    dataset_id: UUID
    status: DecisionStatus = DecisionStatus.PENDING

    class Meta:
        orm_model = DataProductDatasetModel


class DataProductDatasetAssociationUpdate(DataProductDatasetAssociationCreate):
    pass
