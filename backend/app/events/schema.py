from typing import Optional
from uuid import UUID

from app.events.enums import EventReferenceEntity, EventType
from app.events.model import Event as EventModel
from app.shared.schema import ORMModel


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
