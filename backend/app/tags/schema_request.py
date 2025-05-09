from app.shared.schema import ORMModel


class TagCreate(ORMModel):
    value: str


class TagUpdate(TagCreate):
    pass
