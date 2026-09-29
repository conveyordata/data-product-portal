from typing import Annotated

from pydantic import StringConstraints

from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.shared.schema import ORMModel


class OutputPortAccessTypeCreate(ORMModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    description: str = ""
    access_function: OutputPortAccessFunction


class OutputPortAccessTypeUpdate(OutputPortAccessTypeCreate):
    pass
