from typing import Optional
from uuid import UUID

from pydantic import NaiveDatetime

from app.events.enum import EventReferenceEntity
from app.shared.schema import ORMModel
from app.users.schema import User


class Event(ORMModel):
    name: str
    subject_id: UUID
    target_id: Optional[UUID] = None
    subject_type: EventReferenceEntity
    target_type: Optional[EventReferenceEntity] = None
    actor_id: UUID
    id: UUID
    deleted_subject_identifier: Optional[str] = None
    deleted_target_identifier: Optional[str] = None
    actor: User
    created_on: NaiveDatetime
