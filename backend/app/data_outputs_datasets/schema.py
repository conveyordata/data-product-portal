from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.data_outputs.schema_base_get import DataOutputBaseGet
from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.data_outputs_datasets.model import (
    DataOutputDatasetAssociation as DataOutputDatasetModel,
)
from app.datasets.schema import Dataset
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseDataOutputDatasetAssociation(ORMModel):
    dataset_id: UUID = Field(..., description="Unique identifier of the dataset")
    status: DataOutputDatasetLinkStatus = Field(
        DataOutputDatasetLinkStatus.PENDING_APPROVAL,
        description="Status of the data output-dataset link",
    )

    class Meta:
        orm_model = DataOutputDatasetModel


class DataOutputDatasetAssociationCreate(BaseDataOutputDatasetAssociation):
    pass


class DataOutputDatasetAssociationUpdate(BaseDataOutputDatasetAssociation):
    pass


class DataOutputDatasetAssociation(BaseDataOutputDatasetAssociation):
    id: UUID = Field(
        ..., description="Unique identifier for the data output-dataset association"
    )
    data_output_id: UUID = Field(
        ..., description="Unique identifier of the data output"
    )
    dataset: Dataset = Field(..., description="Dataset associated with the data output")
    data_output: DataOutputBaseGet = Field(
        ..., description="Data output associated with the dataset"
    )
    status: DataOutputDatasetLinkStatus = Field(
        ..., description="Status of the data output-dataset link"
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
