from typing import Optional
from uuid import UUID

from app.data_products.schema_base_get import BaseDataProductGet
from app.datasets.schema_get import DatasetGet
from app.events.enum import Type
from app.events.model import Event as EventModel
from app.shared.schema import ORMModel
from app.users.schema import User


class EventCreate(ORMModel):
    name: str
    subject_id: UUID
    target_id: Optional[UUID] = None
    subject_type: Type
    target_type: Optional[Type] = None

    class Meta:
        orm_model = EventModel


class EventUpdate(EventCreate):
    pass


class Event(EventCreate):
    id: UUID
    data_product: Optional[BaseDataProductGet] = None
    user: Optional[User] = None
    dataset: Optional[DatasetGet] = None
