from uuid import UUID

from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.shared.schema import ORMModel


class OutputPortAccessType(ORMModel):
    id: UUID
    name: str
    access_function: OutputPortAccessFunction
