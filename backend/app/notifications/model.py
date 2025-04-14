import uuid

from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.data_outputs_datasets.model import DataOutputDatasetAssociation
from app.data_product_memberships.enums import DataProductMembershipStatus
from app.data_product_memberships.model import DataProductMembership
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
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
    notification_origin: Mapped[DataProductDatasetLinkStatus] = mapped_column(
        Enum(DataProductDatasetLinkStatus), nullable=False, use_existing_column=True
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
    notification_origin: Mapped[DataOutputDatasetLinkStatus] = mapped_column(
        Enum(DataOutputDatasetLinkStatus), nullable=False, use_existing_column=True
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
    notification_origin: Mapped[DataProductMembershipStatus] = mapped_column(
        Enum(DataProductMembershipStatus), nullable=False, use_existing_column=True
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
        db: Session, data_product_dataset: DataProductDatasetAssociation, approved: bool
    ):
        notification = DataProductDatasetNotification(
            notification_type=NotificationTypes.DataProductDatasetNotification,
            notification_origin=(
                DataProductDatasetLinkStatus.APPROVED
                if approved
                else DataProductDatasetLinkStatus.DENIED
            ),
            data_product_dataset_id=data_product_dataset.id,
        )
        receivers = list(
            {
                owner.id: owner
                for owner in (
                    data_product_dataset.dataset.owners
                    + [data_product_dataset.requested_by]
                )
            }.values()
        )
        notification.notification_interactions = [
            NotificationInteraction(user=receiver, notification=notification)
            for receiver in receivers
        ]
        db.add(notification)

    @staticmethod
    def createDataOutputDatasetNotification(
        db: Session, data_output_dataset: DataOutputDatasetAssociation, approved: bool
    ):
        notification = DataOutputDatasetNotification(
            notification_type=NotificationTypes.DataOutputDatasetNotification,
            notification_origin=(
                DataOutputDatasetLinkStatus.APPROVED
                if approved
                else DataOutputDatasetLinkStatus.DENIED
            ),
            data_output_dataset_id=data_output_dataset.id,
        )
        receivers = list(
            {
                owner.id: owner
                for owner in (
                    data_output_dataset.dataset.owners
                    + [data_output_dataset.requested_by]
                )
            }.values()
        )
        notification.notification_interactions = [
            NotificationInteraction(user=receiver, notification=notification)
            for receiver in receivers
        ]
        db.add(notification)

    @staticmethod
    def createDataProductMembershipNotification(
        db: Session, data_product_membership: DataProductMembership, approved: bool
    ):
        notification = DataProductMembershipNotification(
            notification_type=NotificationTypes.DataProductMembershipNotification,
            notification_origin=(
                DataProductMembershipStatus.APPROVED
                if approved
                else DataProductMembershipStatus.DENIED
            ),
            data_product_membership_id=data_product_membership.id,
        )
        receivers = list(
            {
                owner.id: owner
                for owner in (
                    data_product_membership.data_product.owners
                    + [data_product_membership.user]
                )
            }.values()
        )
        notification.notification_interactions = [
            NotificationInteraction(user=receiver, notification=notification)
            for receiver in receivers
        ]
        db.add(notification)
