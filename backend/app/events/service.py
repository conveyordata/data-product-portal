from uuid import UUID

from sqlalchemy import and_, event, or_, select, update
from sqlalchemy.orm import Session

from app.data_outputs.model import DataOutput
from app.data_products.model import DataProduct
from app.datasets.model import Dataset
from app.events.enum import Type
from app.events.model import Event as EventModel
from app.events.schema import EventCreate
from app.users.model import User


@event.listens_for(User, "before_delete")
def _backup_user_name_on_delete(mapper, connection, target):
    connection.execute(
        update(EventModel.__table__)
        .where(
            and_(
                EventModel.subject_id == target.id, EventModel.subject_type == Type.USER
            )
        )
        .values(deleted_subject_identifier=target.email)
    )
    connection.execute(
        update(EventModel.__table__)
        .where(
            and_(EventModel.target_id == target.id, EventModel.target_type == Type.USER)
        )
        .values(deleted_target_identifier=target.email)
    )


@event.listens_for(Dataset, "before_delete")
def _backup_dataset_name_on_delete(mapper, connection, target):
    connection.execute(
        update(EventModel.__table__)
        .where(
            and_(
                EventModel.subject_id == target.id,
                EventModel.subject_type == Type.DATASET,
            )
        )
        .values(deleted_subject_identifier=target.name)
    )
    connection.execute(
        update(EventModel.__table__)
        .where(
            and_(
                EventModel.target_id == target.id,
                EventModel.target_type == Type.DATASET,
            )
        )
        .values(deleted_target_identifier=target.name)
    )


@event.listens_for(DataProduct, "before_delete")
def _backup_data_product_name_on_delete(mapper, connection, target):
    connection.execute(
        update(EventModel.__table__)
        .where(
            and_(
                EventModel.subject_id == target.id,
                EventModel.subject_type == Type.DATA_PRODUCT,
            )
        )
        .values(deleted_subject_identifier=target.name)
    )
    connection.execute(
        update(EventModel.__table__)
        .where(
            and_(
                EventModel.target_id == target.id,
                EventModel.target_type == Type.DATA_PRODUCT,
            )
        )
        .values(deleted_target_identifier=target.name)
    )


@event.listens_for(DataOutput, "before_delete")
def _backup_data_output_name_on_delete(mapper, connection, target):
    connection.execute(
        update(EventModel.__table__)
        .where(
            and_(
                EventModel.subject_id == target.id,
                EventModel.subject_type == Type.DATA_OUTPUT,
            )
        )
        .values(deleted_subject_identifier=target.name)
    )
    connection.execute(
        update(EventModel.__table__)
        .where(
            and_(
                EventModel.target_id == target.id,
                EventModel.target_type == Type.DATA_OUTPUT,
            )
        )
        .values(deleted_target_identifier=target.name)
    )


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
