import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.notifications.model import Notification
from app.shared.model import BaseORM

from .enums import EventReferenceEntity

if TYPE_CHECKING:
    from app.data_outputs.model import DataOutput
    from app.data_products.model import DataProduct
    from app.datasets.model import Dataset
    from app.users.model import User


class Event(Base, BaseORM):
    __tablename__ = "events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    deleted_subject_identifier: Mapped[str] = mapped_column(nullable=True)
    subject_id = Column(UUID(as_uuid=True))
    deleted_target_identifier: Mapped[str] = mapped_column(nullable=True)
    target_id = Column(UUID(as_uuid=True))
    subject_type = Column(Enum(EventReferenceEntity))
    target_type = Column(Enum(EventReferenceEntity))
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    actor: Mapped["User"] = relationship("User")

    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="event",
        foreign_keys="Notification.event_id",
        lazy="raise",
    )

    # Conditional relationships based on subject_type
    data_product: Mapped["DataProduct"] = relationship(
        primaryjoin="or_(and_(Event.subject_id == "
        "foreign(DataProduct.id), Event.subject_type == 'DATA_PRODUCT'), "
        "and_(Event.target_id == foreign(DataProduct.id), "
        "Event.target_type == 'DATA_PRODUCT'))",
    )
    user: Mapped["User"] = relationship(
        primaryjoin="or_(and_(Event.subject_id == "
        "foreign(User.id), Event.subject_type == 'USER')"
        ",and_(Event.target_id == foreign(User.id), "
        "Event.target_type == 'USER'))",
    )
    dataset: Mapped["Dataset"] = relationship(
        primaryjoin="or_(and_(Event.subject_id == foreign(Dataset.id),"
        " Event.subject_type == 'DATASET'),"
        "and_(Event.target_id == foreign(Dataset.id),"
        " Event.target_type == 'DATASET'))",
    )
    data_output: Mapped["DataOutput"] = relationship(
        primaryjoin="or_(and_(Event.subject_id == "
        "foreign(DataOutput.id), Event.subject_type == 'DATA_OUTPUT'),"
        "and_(Event.target_id == foreign(DataOutput.id),"
        " Event.target_type == 'DATA_OUTPUT'))",
    )
