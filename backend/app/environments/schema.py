from app.shared.schema import ORMModel


class Environment(ORMModel):
    name: str
    context: str
    is_default: bool = False
