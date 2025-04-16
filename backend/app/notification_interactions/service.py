import itertools
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, joinedload

from app.data_outputs_datasets.model import DataOutputDatasetAssociation
from app.data_product_memberships.model import DataProductMembership
from app.data_products_datasets.model import DataProductDatasetAssociation
from app.notification_interactions.model import NotificationInteraction
from app.notification_interactions.schema_get import NotificationInteractionGet
from app.notifications.model import (
    DataOutputDatasetNotification,
    DataProductDatasetNotification,
    DataProductMembershipNotification,
)
from app.notifications.notification_types import NotificationTypes
from app.users.schema import User


class NotificationInteractionService:

    def get_user_notification_interactions(
        self, db: Session, authenticated_user: User
    ) -> list[NotificationInteractionGet]:
        return db.scalars(
            select(NotificationInteraction)
            .options(
                joinedload(NotificationInteraction.notification),
                joinedload(NotificationInteraction.user),
            )
            .where(NotificationInteraction.user_id == authenticated_user.id)
            .order_by(desc(NotificationInteraction.created_on))
        ).all()

    def remove_notification_interaction(
        self, id: UUID, db: Session, authenticated_user: User
    ):
        notification_interaction = db.get(
            NotificationInteraction,
            id,
        )
        if not notification_interaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification {id} not found",
            )
        if notification_interaction.user_id != authenticated_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Notification {id} belongs to another user",
            )
        db.delete(notification_interaction)
        db.commit()

    def create_data_product_dataset_notifications(
        self, db: Session, data_product_dataset: DataProductDatasetAssociation
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

    def create_data_output_dataset_notifications(
        self, db: Session, data_output_dataset: DataOutputDatasetAssociation
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

    def create_data_product_membership_notifications(
        self, db: Session, data_product_membership: DataProductMembership
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
