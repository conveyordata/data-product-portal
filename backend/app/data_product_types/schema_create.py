from pydantic import Field

from app.data_product_types.enums import DataProductIconKey
from app.data_product_types.model import DataProductType as DataProductTypeModel
from app.shared.schema import ORMModel


class DataProductTypeCreate(ORMModel):
    name: str = Field(..., description="Name of the data product type")
    description: str = Field(..., description="Description of the data product type")
    icon_key: DataProductIconKey = Field(
        ..., description="Icon key representing the data product type"
    )

    class Meta:
        orm_model = DataProductTypeModel


class DataProductTypeUpdate(DataProductTypeCreate):
    pass
