from typing import Sequence
from uuid import UUID

from app.configuration.output_port_classifications.schema import (
    OutputPortClassification,
)
from app.shared.schema import ORMModel


class OutputPortClassificationsGetItem(OutputPortClassification):
    description: str
    output_port_count: int


class OutputPortClassificationsGet(ORMModel):
    output_port_classifications: Sequence[OutputPortClassificationsGetItem]


class CreateOutputPortClassificationResponse(ORMModel):
    id: UUID


class UpdateOutputPortClassificationResponse(ORMModel):
    id: UUID
