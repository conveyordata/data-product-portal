from typing import Annotated, Optional
from uuid import UUID

from annotated_types import MinLen
from pydantic import Field

from app.datasets.enums import DatasetAccessType
from app.datasets.status import DatasetStatus
from app.domains.schema import Domain
from app.shared.schema import ORMModel
from app.tags.schema import Tag
from app.users.schema import User


class BaseDataset(ORMModel):
    name: str = Field(..., description="Name of the dataset")
    external_id: str = Field(..., description="External identifier for the dataset")
    description: str = Field(..., description="Description of the dataset")
    access_type: DatasetAccessType = Field(
        ..., description="Access type of the dataset"
    )
    about: Optional[str] = Field(
        None, description="Additional information about the dataset"
    )
    lifecycle_id: Optional[UUID] = Field(
        None, description="Lifecycle ID of the dataset"
    )


class DatasetAboutUpdate(ORMModel):
    about: str = Field(..., description="Additional information about the dataset")


class DatasetStatusUpdate(ORMModel):
    status: DatasetStatus = Field(..., description="Current status of the dataset")


class DatasetCreateUpdate(BaseDataset):
    owners: Annotated[list[UUID], MinLen(1)] = Field(
        ..., description="List of UUIDs of the owners of the dataset"
    )
    domain_id: UUID = Field(
        ..., description="UUID of the domain to which the dataset belongs"
    )
    tag_ids: list[UUID] = Field(
        ..., description="List of UUIDs of the tags associated with the dataset"
    )


class Dataset(BaseDataset):
    id: UUID = Field(..., description="Unique identifier for the dataset")
    owners: Annotated[list[User], MinLen(1)] = Field(
        ..., description="List of users who own the dataset"
    )
    status: DatasetStatus = Field(..., description="Current status of the dataset")
    domain: Domain = Field(..., description="Domain to which the dataset belongs")
    tags: list[Tag] = Field(..., description="List of tags associated with the dataset")
