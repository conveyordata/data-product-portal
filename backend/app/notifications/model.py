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
    def createDataProductDatasetApproved(
        db: Session, data_product_dataset: DataProductDatasetAssociation
    ):
        notification = DataProductDatasetNotification(
            notification_type=NotificationTypes.DataProductDatasetNotification,
            notification_origin=DataProductDatasetLinkStatus.APPROVED,
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
    def createDataProductDatasetDenied(
        db: Session, data_product_dataset: DataProductDatasetAssociation
    ):
        notification = DataProductDatasetNotification(
            notification_type=NotificationTypes.DataProductDatasetNotification,
            notification_origin=DataProductDatasetLinkStatus.DENIED,
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
    def createDataProductDatasetRequested(
        db: Session, data_product_dataset: DataProductDatasetAssociation
    ):
        notification = DataProductDatasetNotification(
            notification_type=NotificationTypes.DataProductDatasetNotification,
            notification_origin=DataProductDatasetLinkStatus.APPROVED,
            data_product_dataset_id=data_product_dataset.id,
        )
        receivers = data_product_dataset.dataset.owners
        notification.notification_interactions = [
            NotificationInteraction(user=receiver, notification=notification)
            for receiver in receivers
        ]
        db.add(notification)

    @staticmethod
    def createDataOutputDatasetApproved(
        db: Session, data_output_dataset: DataOutputDatasetAssociation
    ):
        notification = DataOutputDatasetNotification(
            notification_type=NotificationTypes.DataOutputDatasetNotification,
            notification_origin=DataOutputDatasetLinkStatus.APPROVED,
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
    def createDataOutputDatasetDenied(
        db: Session, data_output_dataset: DataOutputDatasetAssociation
    ):
        notification = DataOutputDatasetNotification(
            notification_type=NotificationTypes.DataOutputDatasetNotification,
            notification_origin=DataOutputDatasetLinkStatus.DENIED,
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
    def createDataOutputDatasetRequested(
        db: Session, data_output_dataset: DataOutputDatasetAssociation
    ):
        notification = DataOutputDatasetNotification(
            notification_type=NotificationTypes.DataOutputDatasetNotification,
            notification_origin=DataOutputDatasetLinkStatus.PENDING_APPROVAL,
            data_output_dataset_id=data_output_dataset.id,
        )
        receivers = data_output_dataset.dataset.owners
        notification.notification_interactions = [
            NotificationInteraction(user=receiver, notification=notification)
            for receiver in receivers
        ]
        db.add(notification)

    @staticmethod
    def createDataProductMembershipApproved(
        db: Session, data_product_membership: DataProductMembership
    ):
        notification = DataProductMembershipNotification(
            notification_type=NotificationTypes.DataProductMembershipNotification,
            notification_origin=DataProductMembershipStatus.APPROVED,
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

    @staticmethod
    def createDataProductMembershipDenied(
        db: Session, data_product_membership: DataProductMembership
    ):
        notification = DataProductMembershipNotification(
            notification_type=NotificationTypes.DataProductMembershipNotification,
            notification_origin=DataProductMembershipStatus.DENIED,
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

    @staticmethod
    def createDataProductMembershipRequested(
        db: Session, data_product_membership: DataProductMembership
    ):
        notification = DataProductMembershipNotification(
            notification_type=NotificationTypes.DataProductMembershipNotification,
            notification_origin=DataProductDatasetLinkStatus.PENDING_APPROVAL,
            data_product_membership_id=data_product_membership.id,
        )
        receivers = data_product_membership.data_product.owners
        notification.notification_interactions = [
            NotificationInteraction(user=receiver, notification=notification)
            for receiver in receivers
        ]
        db.add(notification)
