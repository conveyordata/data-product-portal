from app.shared.schema import ORMModel


class GroupCreate(ORMModel):
    external_id: str
    display_name: str


class GroupUpdate(ORMModel):
    external_id: str
    display_name: str