from typing import Annotated, Optional
from uuid import UUID

from annotated_types import MinLen

from app.datasets.enums import OutputPortAccessType
from app.datasets.status import OutputPortStatus
from app.shared.schema import ORMModel


class DatasetUpdate(ORMModel):
    name: str
    namespace: str
    description: str
    access_type: OutputPortAccessType
    about: Optional[str] = None
    lifecycle_id: Optional[UUID] = None
    domain_id: UUID
    tag_ids: list[UUID]


class DatasetCreate(DatasetUpdate):
    data_product_id: UUID
    owners: Annotated[list[UUID], MinLen(1)]


class DatasetAboutUpdate(ORMModel):
    about: str


class DatasetStatusUpdate(ORMModel):
    status: OutputPortStatus


class DatasetUsageUpdate(ORMModel):
    usage: str
