from uuid import UUID
from warnings import deprecated

from app.configuration.access_modes.schema_response import AccessMode
from app.configuration.output_port_access_types.schema import (
    OutputPortAccessType,
)
from app.configuration.tags.schema import Tag
from app.data_products.output_ports.status import OutputPortStatus
from app.shared.schema import ORMModel


class OutputPort(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str
    status: OutputPortStatus
    access_type: OutputPortAccessType
    data_product_id: UUID
    tags: list[Tag]
    access_modes: list[AccessMode]


@deprecated("use OutputPort instead")
class Dataset(OutputPort):
    def convert(self) -> OutputPort:
        return OutputPort(**self.model_dump())
