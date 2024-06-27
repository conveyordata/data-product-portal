from typing import Optional
from uuid import UUID

from app.business_areas.schema import BusinessArea
from app.datasets.enums import DatasetAccessType
from app.shared.schema import ORMModel
from app.tags.schema import TagCreate
from app.users.schema import User


class BaseDataset(ORMModel):
    name: str
    external_id: str
    description: str
    tags: list[TagCreate]
    access_type: DatasetAccessType


class DatasetAboutUpdate(ORMModel):
    about: str


class DatasetCreateUpdate(BaseDataset):
    owners: list[UUID]
    business_area_id: UUID


class Dataset(BaseDataset):
    id: UUID
    owners: list[User]
    business_area: BusinessArea
    about: Optional[str] = None
