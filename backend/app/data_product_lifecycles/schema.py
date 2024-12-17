from uuid import UUID

from app.data_product_lifecycles.model import (
    DataProductLifecycle as DataProductLifeCycleModel,
)
from app.shared.schema import ORMModel


class DataProductLifeCycleCreate(ORMModel):
    value: int
    name: str

    class Meta:
        orm_model = DataProductLifeCycleModel


class DataProductLifeCycle(DataProductLifeCycleCreate):
    id: UUID
