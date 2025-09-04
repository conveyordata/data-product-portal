from datetime import datetime
from typing import Sequence
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import event as sql_event
from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from app.data_outputs.model import DataOutput
from app.data_products.model import DataProduct
from app.datasets.model import Dataset
from app.events.enums import EventReferenceEntity
from app.events.model import Event as EventModel
from app.events.schema import CreateEvent
from app.users.model import User


@sql_event.listens_for(User, "before_delete")
def _backup_user_name_on_delete(mapper, connection, target):
    connection.execute(
        update(EventModel.__table__)
        .where(
            and_(
                EventModel.subject_id == target.id,
                EventModel.subject_type == EventReferenceEntity.USER,
            )
        )
        .values(deleted_subject_identifier=target.email)
    )
    connection.execute(
        update(EventModel.__table__)
        .where(
            and_(
                EventModel.target_id == target.id,
                EventModel.target_type == EventReferenceEntity.USER,
            )
        )
        .values(deleted_target_identifier=target.email)
    )


@sql_event.listens_for(Dataset, "before_delete")
def _backup_dataset_name_on_delete(mapper, connection, target):
    connection.execute(
        update(EventModel.__table__)
        .where(
            and_(
                EventModel.subject_id == target.id,
                EventModel.subject_type == EventReferenceEntity.DATASET,
            )
        )
        .values(deleted_subject_identifier=target.name)
    )
    connection.execute(
        update(EventModel.__table__)
        .where(
            and_(
                EventModel.target_id == target.id,
                EventModel.target_type == EventReferenceEntity.DATASET,
            )
        )
        .values(deleted_target_identifier=target.name)
    )


@sql_event.listens_for(DataProduct, "before_delete")
def _backup_data_product_name_on_delete(mapper, connection, target):
    connection.execute(
        update(EventModel.__table__)
        .where(
            and_(
                EventModel.subject_id == target.id,
                EventModel.subject_type == EventReferenceEntity.DATA_PRODUCT,
            )
        )
        .values(deleted_subject_identifier=target.name)
    )
    connection.execute(
        update(EventModel.__table__)
        .where(
            and_(
                EventModel.target_id == target.id,
                EventModel.target_type == EventReferenceEntity.DATA_PRODUCT,
            )
        )
        .values(deleted_target_identifier=target.name)
    )


@sql_event.listens_for(DataOutput, "before_delete")
def _backup_data_output_name_on_delete(mapper, connection, target):
    connection.execute(
        update(EventModel.__table__)
        .where(
            and_(
                EventModel.subject_id == target.id,
                EventModel.subject_type == EventReferenceEntity.DATA_OUTPUT,
            )
        )
        .values(deleted_subject_identifier=target.name)
    )
    connection.execute(
        update(EventModel.__table__)
        .where(
            and_(
                EventModel.target_id == target.id,
                EventModel.target_type == EventReferenceEntity.DATA_OUTPUT,
            )
        )
        .values(deleted_target_identifier=target.name)
    )


class EventService:
    def __init__(self, db: Session):
        self.db = db

    def create_event(self, event: CreateEvent) -> UUID:
        event = EventModel(**event.parse_pydantic_schema())
        self.db.add(event)
        self.db.flush()
        return event.id

    def get_history(self, id: UUID, type: EventReferenceEntity) -> Sequence[EventModel]:
        return self.db.scalars(
            select(EventModel)
            .where(
                or_(
                    (EventModel.subject_id == id) & (EventModel.subject_type == type),
                    (EventModel.target_id == id) & (EventModel.target_type == type),
                )
            )
            .order_by(EventModel.created_on.desc())
        ).all()

    def get_latest_event_timestamp(self) -> datetime:
        return self.db.scalar(
            select(EventModel.created_on)
            .order_by(EventModel.created_on.desc())
            .limit(1)
        )
