from typing import Optional
from uuid import UUID

from pydantic import NaiveDatetime

from app.data_outputs.schema import DataOutput
from app.data_products.schema import DataProduct
from app.datasets.schema import Dataset
from app.events.enum import EventReferenceEntity
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseEventGet(ORMModel):
    id: UUID
    name: str
    subject_id: UUID
    target_id: Optional[UUID] = None
    subject_type: EventReferenceEntity
    target_type: Optional[EventReferenceEntity] = None
    actor_id: UUID
    created_on: NaiveDatetime


class EventGet(BaseEventGet):
    deleted_subject_identifier: Optional[str] = None
    deleted_target_identifier: Optional[str] = None
    actor: User
    data_product: Optional[DataProduct] = None
    user: Optional[User] = None
    dataset: Optional[Dataset] = None
    data_output: Optional[DataOutput] = None
