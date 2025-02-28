from typing import Optional
from uuid import UUID

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
    owners: list[UUID]
    domain_id: UUID
    tag_ids: list[UUID]


class Dataset(BaseDataset):
    id: UUID
    owners: list[User]
    status: DatasetStatus
    domain: Domain
    tags: list[Tag]
