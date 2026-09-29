from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.shared.schema import ORMModel


class OutputPortClassificationCreate(ORMModel):
    name: str
    description: str = ""
    access_function: OutputPortAccessFunction


class OutputPortClassificationUpdate(OutputPortClassificationCreate):
    pass
