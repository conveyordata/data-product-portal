from app.data_product_types.enums import DataProductIconKey
from app.data_product_types.model import DataProductType as DataProductTypeModel
from app.shared.schema import ORMModel


class DataProductTypeCreate(ORMModel):
    name: str
    description: str
    icon_key: DataProductIconKey

    class Meta:
        orm_model = DataProductTypeModel
