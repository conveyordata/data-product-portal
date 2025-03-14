from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.data_products.schema_base_get import BaseDataProductGet
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetModel,
)
from app.datasets.schema import Dataset
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseDataProductDatasetAssociation(ORMModel):
    dataset_id: UUID = Field(..., description="Unique identifier of the dataset")
    status: DataProductDatasetLinkStatus = Field(
        DataProductDatasetLinkStatus.PENDING_APPROVAL,
        description="Status of the data product-dataset link",
    )

    class Meta:
        orm_model = DataProductDatasetModel


class DataProductDatasetAssociationCreate(BaseDataProductDatasetAssociation):
    pass


class DataProductDatasetAssociationUpdate(BaseDataProductDatasetAssociation):
    pass


class DataProductDatasetAssociation(BaseDataProductDatasetAssociation):
    id: UUID = Field(
        ..., description="Unique identifier for the data product-dataset association"
    )
    data_product_id: UUID = Field(
        ..., description="Unique identifier of the data product"
    )
    dataset: Dataset = Field(
        ..., description="Dataset associated with the data product"
    )
    data_product: BaseDataProductGet = Field(
        ..., description="Data product associated with the dataset"
    )
    status: DataProductDatasetLinkStatus = Field(
        ..., description="Status of the data product-dataset link"
    )
    requested_by: User = Field(..., description="User who requested the association")
    denied_by: User | None = Field(
        None, description="User who denied the association, if applicable"
    )
    approved_by: User | None = Field(
        None, description="User who approved the association, if applicable"
    )
    requested_on: datetime = Field(
        ..., description="Timestamp when the association was requested"
    )
    denied_on: datetime | None = Field(
        None, description="Timestamp when the association was denied, if applicable"
    )
    approved_on: datetime | None = Field(
        None, description="Timestamp when the association was approved, if applicable"
    )


class DatasetDataProductLink(DataProductDatasetAssociation):
    dataset: Dataset = Field(
        ..., description="Dataset associated with the data product"
    )
