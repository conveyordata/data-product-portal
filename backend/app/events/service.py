from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.events.enum import Type
from app.events.model import Event as EventModel
from app.events.schema import EventCreate


class EventService:
    def create_event(self, db: Session, event: EventCreate):
        event = EventModel(**event.parse_pydantic_schema())
        db.add(event)
        db.commit()
        return {"id": event.id}

    def get_history(self, db: Session, id: UUID, type: Type):
        return db.scalars(
            select(EventModel)
            .where(
                or_(
                    (EventModel.subject_id == id) & (EventModel.subject_type == type),
                    (EventModel.target_id == id) & (EventModel.target_type == type),
                )
            )
            .order_by(EventModel.created_on.desc())
        ).all()

    def get_domain_history(self, db: Session, domain_id: UUID):
        return db.scalars(
            select(EventModel)
            .where(EventModel.domain_id == domain_id)
            .order_by(EventModel.created_on.desc())
        ).all()

    def get_user_history(self, db: Session, user_id: UUID):
        return db.scalars(
            select(EventModel)
            .where(EventModel.actor_id == user_id)
            .order_by(EventModel.created_on.desc())
        ).all()
