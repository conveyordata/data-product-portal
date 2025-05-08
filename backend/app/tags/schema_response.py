from uuid import UUID

from app.shared.schema import ORMModel


class BaseTagGet(ORMModel):
    id: UUID
    value: str


class TagGet(BaseTagGet):
    pass


class TagsGet(BaseTagGet):
    pass
