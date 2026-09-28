from app.data_products.output_ports.enums import OutputPortAccessType
from app.shared.schema import ORMModel


class OutputPortClassificationCreate(ORMModel):
    name: str
    description: str = ""
    access_type: OutputPortAccessType


class OutputPortClassificationUpdate(OutputPortClassificationCreate):
    pass
