from typing import Sequence
from uuid import UUID

from app.shared.schema import ORMModel


class BaseDataProductLifeCycleGet(ORMModel):
    id: UUID
    value: int
    name: str
    color: str
    is_default: bool


class DataProductLifeCycleGet(BaseDataProductLifeCycleGet):
    pass


class DataProductLifeCyclesGetItem(BaseDataProductLifeCycleGet):
    pass


class DataProductLifeCyclesGet(ORMModel):
    data_product_life_cycles: Sequence[DataProductLifeCyclesGetItem]
