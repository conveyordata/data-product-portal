from typing import Optional
from uuid import UUID

from pydantic import NaiveDatetime

from app.events.enums import EventReferenceEntity, EventType
from app.events.model import Event as EventModel
from app.shared.schema import ORMModel
from app.users.schema import User


class CreateEvent(ORMModel):
    name: EventType
    actor_id: UUID
    subject_id: UUID
    subject_type: EventReferenceEntity
    target_id: Optional[UUID] = None
    target_type: Optional[EventReferenceEntity] = None
    deleted_subject_identifier: Optional[str] = None
    deleted_target_identifier: Optional[str] = None

    class Meta:
        orm_model = EventModel


class Event(ORMModel):
    id: UUID
    name: EventType
    actor: User
    actor_id: UUID
    subject_id: UUID
    subject_type: EventReferenceEntity
    target_id: Optional[UUID] = None
    target_type: Optional[EventReferenceEntity] = None
    deleted_subject_identifier: Optional[str] = None
    deleted_target_identifier: Optional[str] = None
    created_on: NaiveDatetime
