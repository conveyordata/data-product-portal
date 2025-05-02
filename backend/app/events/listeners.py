from sqlalchemy import and_, event, update

from app.data_outputs.model import DataOutput
from app.data_products.model import DataProduct
from app.datasets.model import Dataset
from app.events.enum import Type
from app.events.model import Event
from app.users.model import User


@event.listens_for(User, "before_delete")
def _backup_user_name_on_delete(mapper, connection, target):
    connection.execute(
        update(Event.__table__)
        .where(and_(Event.subject_id == target.id, Event.subject_type == Type.USER))
        .values(deleted_subject_identifier=target.email)
    )
    connection.execute(
        update(Event.__table__)
        .where(and_(Event.target_id == target.id, Event.target_type == Type.USER))
        .values(deleted_target_identifier=target.email)
    )


@event.listens_for(Dataset, "before_delete")
def _backup_dataset_name_on_delete(mapper, connection, target):
    connection.execute(
        update(Event.__table__)
        .where(and_(Event.subject_id == target.id, Event.subject_type == Type.DATASET))
        .values(deleted_subject_identifier=target.name)
    )
    connection.execute(
        update(Event.__table__)
        .where(and_(Event.target_id == target.id, Event.target_type == Type.DATASET))
        .values(deleted_target_identifier=target.name)
    )


@event.listens_for(DataProduct, "before_delete")
def _backup_data_product_name_on_delete(mapper, connection, target):
    connection.execute(
        update(Event.__table__)
        .where(
            and_(Event.subject_id == target.id, Event.subject_type == Type.DATA_PRODUCT)
        )
        .values(deleted_subject_identifier=target.name)
    )
    connection.execute(
        update(Event.__table__)
        .where(
            and_(Event.target_id == target.id, Event.target_type == Type.DATA_PRODUCT)
        )
        .values(deleted_target_identifier=target.name)
    )


@event.listens_for(DataOutput, "before_delete")
def _backup_data_output_name_on_delete(mapper, connection, target):
    connection.execute(
        update(Event.__table__)
        .where(
            and_(Event.subject_id == target.id, Event.subject_type == Type.DATA_OUTPUT)
        )
        .values(deleted_subject_identifier=target.name)
    )
    connection.execute(
        update(Event.__table__)
        .where(
            and_(Event.target_id == target.id, Event.target_type == Type.DATA_OUTPUT)
        )
        .values(deleted_target_identifier=target.name)
    )
