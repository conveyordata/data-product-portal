from typing import Annotated, Optional
from uuid import UUID

from annotated_types import MinLen

from app.access_durations.enums import AccessDurationType
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.status import OutputPortStatus
from app.shared.schema import ORMModel


class DatasetUpdate(ORMModel):
    name: str
    namespace: str
    description: str
    access_type: OutputPortAccessType
    data_product_access_duration_type: AccessDurationType
    exploration_access_duration_type: AccessDurationType
    about: Optional[str] = None
    lifecycle_id: Optional[UUID] = None
    tag_ids: list[UUID]


class CreateOutputPortRequest(DatasetUpdate):
    owners: Annotated[list[UUID], MinLen(1)]


class DatasetAboutUpdate(ORMModel):
    about: str


class DatasetStatusUpdate(ORMModel):
    status: OutputPortStatus


class DatasetUsageUpdate(ORMModel):
    usage: str
