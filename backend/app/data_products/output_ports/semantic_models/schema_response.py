from uuid import UUID

from app.data_products.output_ports.semantic_models.model import SemanticModelFormat
from app.shared.schema import ORMModel


class SemanticModelResponse(ORMModel):
    id: UUID
    output_port_id: UUID
    name: str
    format: SemanticModelFormat
    content: dict
