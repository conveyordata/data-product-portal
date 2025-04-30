from app.data_product_lifecycles.model import (
    DataProductLifecycle as DataProductLifeCycleModel,
)
from app.shared.schema import ORMModel


class DataProductLifeCycleCreate(ORMModel):
    value: int
    name: str
    color: str
    is_default: bool = False

    class Meta:
        orm_model = DataProductLifeCycleModel


class DataProductLifeCycleUpdate(DataProductLifeCycleCreate):
    pass
