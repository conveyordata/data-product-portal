from typing import Optional
from uuid import UUID

from app.business_areas.schema import BusinessArea
from app.datasets.enums import DatasetAccessType
from app.shared.schema import ORMModel
from app.tags.schema import Tag
from app.users.schema import User


class BaseDataset(ORMModel):
    name: str
    external_id: str
    description: str
    access_type: DatasetAccessType
    about: Optional[str] = None


class DatasetAboutUpdate(ORMModel):
    about: str


class DatasetCreateUpdate(BaseDataset):
    owners: list[UUID]
    business_area_id: UUID
    tag_ids: list[UUID]


class Dataset(BaseDataset):
    id: UUID
    owners: list[User]
    business_area: BusinessArea
    tags: list[Tag]
