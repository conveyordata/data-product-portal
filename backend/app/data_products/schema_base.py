from typing import Optional
from uuid import UUID

from pydantic import Field

from app.shared.schema import ORMModel


class BaseDataProduct(ORMModel):
    name: str = Field(..., description="Name of the data product")
    external_id: str = Field(
        ..., description="External identifier for the data product"
    )
    description: str = Field(..., description="Description of the data product")
    type_id: UUID = Field(
        ..., description="Unique identifier for the type of the data product"
    )
    about: Optional[str] = Field(
        None, description="Additional information about the data product"
    )
