from typing import Optional
from uuid import UUID

from pydantic import NaiveDatetime

from app.data_outputs.schema_get import DataOutputGet
from app.data_products.schema_base_get import BaseDataProductGet
from app.datasets.schema_get import DatasetGet
from app.domains.schema import Domain
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
    actor_id: UUID
    domain_id: Optional[UUID] = None

    class Meta:
        orm_model = EventModel


class EventUpdate(EventCreate):
    pass


class Event(EventCreate):
    id: UUID
    actor: User
    data_product: Optional[BaseDataProductGet] = None
    user: Optional[User] = None
    domain: Optional[Domain] = None
    dataset: Optional[DatasetGet] = None
    data_output: Optional[DataOutputGet] = None
    created_on: NaiveDatetime
