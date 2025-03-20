import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.database.database import Base
from app.events.enum import Type
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.data_outputs.model import DataOutput
    from app.data_products.model import DataProduct
    from app.datasets.model import Dataset
    from app.domains.model import Domain
    from app.users.model import User


class Event(Base, BaseORM):
    __tablename__ = "events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    subject_id = Column(UUID(as_uuid=True))
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
        # back_populates="events",
        primaryjoin="or_(and_(Event.subject_id == "
        "foreign(DataProduct.id), Event.subject_type == 'DATA_PRODUCT'), "
        "and_(Event.target_id == foreign(DataProduct.id), "
        "Event.target_type == 'DATA_PRODUCT'))",
    )
    user: Mapped["User"] = relationship(
        "User",
        # back_populates="events",
        primaryjoin="or_(and_(Event.subject_id == "
        "foreign(User.id), Event.subject_type == 'USER')"
        ",and_(Event.target_id == foreign(User.id), "
        "Event.target_type == 'USER'))",
    )
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        # back_populates="events",
        primaryjoin="or_(and_(Event.subject_id == foreign(Dataset.id),"
        " Event.subject_type == 'DATASET'),"
        "and_(Event.target_id == foreign(Dataset.id),"
        " Event.target_type == 'DATASET'))",
    )
    data_output: Mapped["DataOutput"] = relationship(
        "DataOutput",
        # back_populates="events",
        primaryjoin="or_(and_(Event.subject_id == "
        "foreign(DataOutput.id), Event.subject_type == 'DATA_OUTPUT'),"
        "and_(Event.target_id == foreign(DataOutput.id),"
        " Event.target_type == 'DATA_OUTPUT'))",
    )
