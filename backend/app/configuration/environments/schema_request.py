from app.shared.schema import ORMModel


class EnvironmentUpdateGlobal(ORMModel):
    is_global: bool
