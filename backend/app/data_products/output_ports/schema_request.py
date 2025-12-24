from typing import Annotated, Optional
from uuid import UUID
from warnings import deprecated

from annotated_types import MinLen

from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.status import OutputPortStatus
from app.shared.schema import ORMModel


class DatasetUpdate(ORMModel):
    name: str
    namespace: str
    description: str
    access_type: OutputPortAccessType
    about: Optional[str] = None
    lifecycle_id: Optional[UUID] = None
    tag_ids: list[UUID]


class CreateOutputPortRequest(DatasetUpdate):
    owners: Annotated[list[UUID], MinLen(1)]


@deprecated("Use CreateOutputPortRequest instead")
class DatasetCreate(DatasetUpdate):
    data_product_id: UUID
    owners: Annotated[list[UUID], MinLen(1)]

    def convert(self) -> CreateOutputPortRequest:
        return CreateOutputPortRequest(**self.model_dump(exclude={"data_product_id"}))


class DatasetAboutUpdate(ORMModel):
    about: str


class DatasetStatusUpdate(ORMModel):
    status: OutputPortStatus


class DatasetUsageUpdate(ORMModel):
    usage: str
