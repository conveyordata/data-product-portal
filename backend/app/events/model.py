import uuid

from sqlalchemy import Column, Enum, ForeignKey, String, and_, event, update
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data_outputs.model import DataOutput
from app.data_products.model import DataProduct
from app.database.database import Base
from app.datasets.model import Dataset
from app.domains.model import Domain
from app.events.enum import Type
from app.shared.model import BaseORM
from app.users.model import User


class Event(Base, BaseORM):
    __tablename__ = "events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    deleted_subject_identifier: Mapped[str] = mapped_column(nullable=True)
    subject_id = Column(UUID(as_uuid=True))
    deleted_target_identifier: Mapped[str] = mapped_column(nullable=True)
    target_id = Column(UUID(as_uuid=True))
    subject_type = Column(Enum(Type))
    target_type = Column(Enum(Type))
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"))
    domain: Mapped["Domain"] = relationship("Domain")
    actor: Mapped["User"] = relationship("User")

    # Conditional relationships based on subject_type
    data_product: Mapped["DataProduct"] = relationship(
        "DataProduct",
        primaryjoin="or_(and_(Event.subject_id == "
        "foreign(DataProduct.id), Event.subject_type == 'DATA_PRODUCT'), "
        "and_(Event.target_id == foreign(DataProduct.id), "
        "Event.target_type == 'DATA_PRODUCT'))",
    )
    user: Mapped["User"] = relationship(
        "User",
        primaryjoin="or_(and_(Event.subject_id == "
        "foreign(User.id), Event.subject_type == 'USER')"
        ",and_(Event.target_id == foreign(User.id), "
        "Event.target_type == 'USER'))",
    )
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        primaryjoin="or_(and_(Event.subject_id == foreign(Dataset.id),"
        " Event.subject_type == 'DATASET'),"
        "and_(Event.target_id == foreign(Dataset.id),"
        " Event.target_type == 'DATASET'))",
    )
    data_output: Mapped["DataOutput"] = relationship(
        "DataOutput",
        primaryjoin="or_(and_(Event.subject_id == "
        "foreign(DataOutput.id), Event.subject_type == 'DATA_OUTPUT'),"
        "and_(Event.target_id == foreign(DataOutput.id),"
        " Event.target_type == 'DATA_OUTPUT'))",
    )

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
            .where(
                and_(Event.subject_id == target.id, Event.subject_type == Type.DATASET)
            )
            .values(deleted_subject_identifier=target.name)
        )
        connection.execute(
            update(Event.__table__)
            .where(
                and_(Event.target_id == target.id, Event.target_type == Type.DATASET)
            )
            .values(deleted_target_identifier=target.name)
        )

    @event.listens_for(DataProduct, "before_delete")
    def _backup_data_product_name_on_delete(mapper, connection, target):
        connection.execute(
            update(Event.__table__)
            .where(
                and_(
                    Event.subject_id == target.id,
                    Event.subject_type == Type.DATA_PRODUCT,
                )
            )
            .values(deleted_subject_identifier=target.name)
        )
        connection.execute(
            update(Event.__table__)
            .where(
                and_(
                    Event.target_id == target.id, Event.target_type == Type.DATA_PRODUCT
                )
            )
            .values(deleted_target_identifier=target.name)
        )

    @event.listens_for(DataOutput, "before_delete")
    def _backup_data_output_name_on_delete(mapper, connection, target):
        connection.execute(
            update(Event.__table__)
            .where(
                and_(
                    Event.subject_id == target.id,
                    Event.subject_type == Type.DATA_OUTPUT,
                )
            )
            .values(deleted_subject_identifier=target.name)
        )
        connection.execute(
            update(Event.__table__)
            .where(
                and_(
                    Event.target_id == target.id, Event.target_type == Type.DATA_OUTPUT
                )
            )
            .values(deleted_target_identifier=target.name)
        )
