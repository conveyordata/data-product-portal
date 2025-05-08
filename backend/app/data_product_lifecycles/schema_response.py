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


class DataProductLifeCyclesGet(BaseDataProductLifeCycleGet):
    pass
