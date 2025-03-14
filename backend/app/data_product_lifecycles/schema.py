from uuid import UUID

from pydantic import Field

from app.data_product_lifecycles.model import (
    DataProductLifecycle as DataProductLifeCycleModel,
)
from app.shared.schema import ORMModel


class DataProductLifeCycleCreate(ORMModel):
    value: int = Field(..., description="Value representing the lifecycle stage")
    name: str = Field(..., description="Name of the lifecycle stage")
    color: str = Field(..., description="Color associated with the lifecycle stage")
    is_default: bool = Field(
        False, description="Indicates if this is the default lifecycle stage"
    )

    class Meta:
        orm_model = DataProductLifeCycleModel


class DataProductLifeCycleUpdate(DataProductLifeCycleCreate):
    pass


class DataProductLifeCycle(DataProductLifeCycleCreate):
    id: UUID = Field(
        ..., description="Unique identifier for the data product lifecycle"
    )
