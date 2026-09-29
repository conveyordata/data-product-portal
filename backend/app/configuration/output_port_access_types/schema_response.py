from typing import Sequence
from uuid import UUID

from app.configuration.output_port_access_types.schema import (
    OutputPortAccessType,
)
from app.shared.schema import ORMModel


class OutputPortAccessTypesGetItem(OutputPortAccessType):
    description: str
    output_port_count: int


class OutputPortAccessTypesGet(ORMModel):
    output_port_access_types: Sequence[OutputPortAccessTypesGetItem]


class CreateOutputPortAccessTypeResponse(ORMModel):
    id: UUID


class UpdateOutputPortAccessTypeResponse(ORMModel):
    id: UUID
