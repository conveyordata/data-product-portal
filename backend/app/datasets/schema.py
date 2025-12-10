from uuid import UUID
from warnings import deprecated

from app.datasets.enums import OutputPortAccessType
from app.datasets.status import OutputPortStatus
from app.shared.schema import ORMModel


class OutputPort(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str
    status: OutputPortStatus
    access_type: OutputPortAccessType
    data_product_id: UUID


@deprecated("use OutputPort instead")
class Dataset(OutputPort):
    def convert(self) -> OutputPort:
        return OutputPort(**self.model_dump())
