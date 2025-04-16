import itertools
import uuid

from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.data_outputs_datasets.model import DataOutputDatasetAssociation
from app.data_product_memberships.model import DataProductMembership
from app.data_products_datasets.model import DataProductDatasetAssociation
from app.database.database import Base
from app.notification_interactions.model import NotificationInteraction
from app.notifications.notification_types import NotificationTypes
from app.shared.model import BaseORM


class Notification(Base, BaseORM):
    __tablename__ = "notifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_type: Mapped[NotificationTypes] = Column(Enum(NotificationTypes))
    notification_interactions: Mapped[list["NotificationInteraction"]] = relationship(
        "NotificationInteraction",
        back_populates="notification",
        cascade="all, delete-orphan",
    )
    __mapper_args__ = {
        "polymorphic_on": "notification_type",
        "polymorphic_identity": "notification",
    }


class DataProductDatasetNotification(Notification):
    data_product_dataset_id: Mapped[UUID] = mapped_column(
        "data_product_dataset_id",
        ForeignKey("data_products_datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    data_product_dataset: Mapped["DataProductDatasetAssociation"] = relationship(
        "DataProductDatasetAssociation",
        back_populates="notifications",
        passive_deletes=True,
    )
    __mapper_args__ = {
        "polymorphic_identity": "DataProductDatasetNotification",
    }


class DataOutputDatasetNotification(Notification):
    data_output_dataset_id: Mapped[UUID] = mapped_column(
        "data_output_dataset_id",
        ForeignKey("data_outputs_datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    data_output_dataset: Mapped["DataOutputDatasetAssociation"] = relationship(
        "DataOutputDatasetAssociation",
        back_populates="notifications",
        passive_deletes=True,
    )
    __mapper_args__ = {
        "polymorphic_identity": "DataOutputDatasetNotification",
    }


class DataProductMembershipNotification(Notification):
    data_product_membership_id: Mapped[UUID] = mapped_column(
        "data_product_membership_id",
        ForeignKey("data_product_memberships.id", ondelete="CASCADE"),
        nullable=False,
    )
    data_product_membership: Mapped["DataProductMembership"] = relationship(
        "DataProductMembership",
        back_populates="notifications",
        passive_deletes=True,
    )
    __mapper_args__ = {
        "polymorphic_identity": "DataProductMembershipNotification",
    }


class NotificationFactory:
    @staticmethod
    def createDataProductDatasetNotification(
        db: Session, data_product_dataset: DataProductDatasetAssociation
    ):
        notification = DataProductDatasetNotification(
            notification_type=NotificationTypes.DataProductDatasetNotification,
            data_product_dataset_id=data_product_dataset.id,
        )
        receivers = set(
            owner.id
            for owner in (
                itertools.chain(
                    data_product_dataset.dataset.owners,
                    [data_product_dataset.requested_by],
                )
            )
        )
        notification.notification_interactions = [
            NotificationInteraction(user_id=receiver, notification=notification)
            for receiver in receivers
        ]
        db.add(notification)

    @staticmethod
    def createDataOutputDatasetNotification(
        db: Session, data_output_dataset: DataOutputDatasetAssociation
    ):
        notification = DataOutputDatasetNotification(
            notification_type=NotificationTypes.DataOutputDatasetNotification,
            data_output_dataset_id=data_output_dataset.id,
        )
        receivers = set(
            owner.id
            for owner in (
                itertools.chain(
                    data_output_dataset.dataset.owners,
                    [data_output_dataset.requested_by],
                )
            )
        )
        notification.notification_interactions = [
            NotificationInteraction(user_id=receiver, notification=notification)
            for receiver in receivers
        ]
        db.add(notification)

    @staticmethod
    def createDataProductMembershipNotification(
        db: Session, data_product_membership: DataProductMembership
    ):
        notification = DataProductMembershipNotification(
            notification_type=NotificationTypes.DataProductMembershipNotification,
            data_product_membership_id=data_product_membership.id,
        )
        receivers = set(
            owner.id
            for owner in (
                itertools.chain(
                    data_product_membership.data_product.owners,
                    [data_product_membership.user],
                )
            )
        )
        notification.notification_interactions = [
            NotificationInteraction(user_id=receiver, notification=notification)
            for receiver in receivers
        ]
        db.add(notification)
