from app.shared.schema import ORMModel


class Environment(ORMModel):
    name: str
    is_default: bool = False
