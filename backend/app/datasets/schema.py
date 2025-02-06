from typing import Optional
from uuid import UUID

from app.business_areas.schema import BusinessArea
from app.datasets.enums import DatasetAccessType
from app.datasets.status import DatasetStatus
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
    business_area_id: UUID
    tag_ids: list[UUID]


class Dataset(BaseDataset):
    id: UUID
    owners: list[User]
    status: DatasetStatus
    business_area: BusinessArea
    tags: list[Tag]
