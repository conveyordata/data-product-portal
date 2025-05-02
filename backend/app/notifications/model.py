import uuid

from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data_outputs_datasets.model import DataOutputDatasetAssociation
from app.data_product_memberships.model import DataProductMembership
from app.data_products_datasets.model import DataProductDatasetAssociation
from app.database.database import Base
from app.notifications.enums import NotificationTypes
from app.role_assignments.enums import DecisionStatus
from app.shared.model import BaseORM
from app.users.model import User


class Notification(Base, BaseORM):
    __tablename__ = "notifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_type: Mapped[NotificationTypes] = Column(Enum(NotificationTypes))
    notification_origin: Mapped[DecisionStatus] = mapped_column(
        Enum(DecisionStatus), nullable=False
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship("User")
    __mapper_args__ = {
        "polymorphic_on": "notification_type",
        "polymorphic_identity": "notification",
    }


class DataProductDatasetNotification(Notification):
    data_product_dataset_id = Column(UUID(as_uuid=True))
    data_product_dataset: Mapped["DataProductDatasetAssociation"] = relationship(
        "DataProductDatasetAssociation",
        primaryjoin=(
            "DataProductDatasetNotification.data_product_dataset_id == "
            "foreign(DataProductDatasetAssociation.id)"
        ),
        viewonly=True,
    )
    deleted_data_product_identifier: Mapped[str] = mapped_column(
        nullable=True, use_existing_column=True
    )
    deleted_dataset_identifier: Mapped[str] = mapped_column(
        nullable=True, use_existing_column=True
    )
    __mapper_args__ = {
        "polymorphic_identity": "DataProductDatasetNotification",
    }


class DataOutputDatasetNotification(Notification):
    data_output_dataset_id = Column(UUID(as_uuid=True))
    data_output_dataset: Mapped["DataOutputDatasetAssociation"] = relationship(
        "DataOutputDatasetAssociation",
        primaryjoin=(
            "DataOutputDatasetNotification.data_output_dataset_id == "
            "foreign(DataOutputDatasetAssociation.id)"
        ),
        viewonly=True,
    )
    deleted_data_output_identifier: Mapped[str] = mapped_column(nullable=True)
    deleted_dataset_identifier: Mapped[str] = mapped_column(
        nullable=True, use_existing_column=True
    )
    __mapper_args__ = {
        "polymorphic_identity": "DataOutputDatasetNotification",
    }


class DataProductMembershipNotification(Notification):
    data_product_membership_id = Column(UUID(as_uuid=True))
    data_product_membership: Mapped["DataProductMembership"] = relationship(
        "DataProductMembership",
        primaryjoin=(
            "DataProductMembershipNotification.data_product_membership_id == "
            "foreign(DataProductMembership.id)"
        ),
        viewonly=True,
    )
    deleted_data_product_identifier: Mapped[str] = mapped_column(
        nullable=True, use_existing_column=True
    )
    __mapper_args__ = {
        "polymorphic_identity": "DataProductMembershipNotification",
    }
