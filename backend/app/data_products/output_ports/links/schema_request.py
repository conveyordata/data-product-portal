from uuid import UUID

from app.authorization.role_assignments.enums import DecisionStatus
from app.data_products.output_ports.links.model import (
    DataProductDatasetAssociation as DataProductDatasetModel,
)
from app.shared.schema import ORMModel


class DataProductDatasetAssociationCreate(ORMModel):
    dataset_id: UUID
    status: DecisionStatus = DecisionStatus.PENDING

    class Meta:
        orm_model = DataProductDatasetModel


class DataProductDatasetAssociationUpdate(DataProductDatasetAssociationCreate):
    pass


class ApproveOutputPortAsInputPortRequest(ORMModel):
    consuming_data_product_id: UUID


class DenyOutputPortAsInputPortRequest(ORMModel):
    consuming_data_product_id: UUID


class RemoveOutputPortAsInputPortRequest(ORMModel):
    consuming_data_product_id: UUID
