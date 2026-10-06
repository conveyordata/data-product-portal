from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.shared.schema import ORMModel, NonEmptyStr


class OutputPortAccessTypeCreate(ORMModel):
    name: NonEmptyStr
    description: str = ""
    access_function: OutputPortAccessFunction


class OutputPortAccessTypeUpdate(OutputPortAccessTypeCreate):
    pass
