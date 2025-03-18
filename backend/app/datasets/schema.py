from typing import Annotated, Optional
from uuid import UUID

from annotated_types import MinLen

from app.datasets.enums import DatasetAccessType
from app.datasets.status import DatasetStatus
from app.domains.schema import Domain
from app.shared.schema import ORMModel
from app.tags.schema import Tag
from app.users.schema import User


class BaseDataset(ORMModel):
    name: str
    external_id: str
    description: str
    access_type: DatasetAccessType
    about: Optional[str] = None
    lifecycle_id: Optional[UUID] = None


class DatasetAboutUpdate(ORMModel):
    about: str


class DatasetStatusUpdate(ORMModel):
    status: DatasetStatus


class DatasetCreateUpdate(BaseDataset):
    owners: Annotated[list[UUID], MinLen(1)]
    domain_id: UUID
    tag_ids: list[UUID]


class Dataset(BaseDataset):
    id: UUID
    owners: Annotated[list[User], MinLen(1)]
    status: DatasetStatus
    domain: Domain
    tags: list[Tag]
