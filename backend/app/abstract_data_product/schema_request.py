from app.shared.schema import ORMModel


class FinalizerRequest(ORMModel):
    finalizer: str
