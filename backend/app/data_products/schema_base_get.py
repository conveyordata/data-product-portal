from typing import Optional
from uuid import UUID

from pydantic import Field

from app.data_product_types.schema_create import DataProductTypeCreate
from app.data_products.status import DataProductStatus
from app.shared.schema import ORMModel


class BaseDataProductGet(ORMModel):
    id: UUID = Field(..., description="Unique identifier for the data product")
    name: str = Field(..., description="Name of the data product")
    description: str = Field(..., description="Description of the data product")
    about: Optional[str] = Field(
        None, description="Additional information about the data product"
    )
    external_id: str = Field(
        ..., description="External identifier for the data product"
    )
    status: DataProductStatus = Field(
        ..., description="Current status of the data product"
    )
    type: DataProductTypeCreate = Field(..., description="Type of the data product")
