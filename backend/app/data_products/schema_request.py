from typing import Annotated, Optional
from uuid import UUID

from annotated_types import MinLen

from app.data_products.status import DataProductStatus
from app.shared.schema import ORMModel


class DataProductUpdate(ORMModel):
    name: str
    namespace: str
    description: str
    type_id: UUID
    about: Optional[str] = None
    domain_id: UUID
    tag_ids: list[UUID]
    lifecycle_id: UUID


class DataProductCreate(DataProductUpdate):
    owners: Annotated[list[UUID], MinLen(1)]


class DataProductAboutUpdate(ORMModel):
    about: str


class DataProductStatusUpdate(ORMModel):
    status: DataProductStatus
