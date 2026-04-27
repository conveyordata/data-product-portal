from app.data_products.output_ports.semantic_models.model import SemanticModelFormat
from app.shared.schema import ORMModel


class SemanticModelRequest(ORMModel):
    name: str
    format: SemanticModelFormat
    content: dict
