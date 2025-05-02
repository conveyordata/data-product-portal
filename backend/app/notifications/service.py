import itertools
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, joinedload

from app.data_outputs_datasets.model import DataOutputDatasetAssociation
from app.data_product_memberships.model import DataProductMembership
from app.data_products_datasets.model import DataProductDatasetAssociation
from app.notifications.enums import NotificationTypes
from app.notifications.model import (
    DataOutputDatasetNotification,
    DataProductDatasetNotification,
    DataProductMembershipNotification,
)
from app.notifications.model import Notification as NotificationModel
from app.notifications.schema import Notification
from app.users.schema import User


class NotificationService:
    def get_user_notifications(
        self, db: Session, authenticated_user: User
    ) -> list[Notification]:
        return db.scalars(
            select(NotificationModel)
            .options(
                joinedload(NotificationModel.user),
            )
            .where(NotificationModel.user_id == authenticated_user.id)
            .order_by(desc(NotificationModel.created_on))
        ).all()

    def remove_notification(self, id: UUID, db: Session, authenticated_user: User):
        notification = db.get(
            NotificationModel,
            id,
        )
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification {id} not found",
            )
        if notification.user_id != authenticated_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Notification {id} belongs to another user",
            )
        db.delete(notification)
        db.commit()

    def create_data_product_dataset_notifications(
        self, db: Session, data_product_dataset: DataProductDatasetAssociation
    ):
        receivers = set(
            owner.id
            for owner in (
                itertools.chain(
                    data_product_dataset.dataset.owners,
                    [data_product_dataset.requested_by],
                )
            )
        )
        for receiver in receivers:
            notification = DataProductDatasetNotification(
                notification_type=NotificationTypes.DataProductDatasetNotification,
                notification_origin=data_product_dataset.status,
                data_product_dataset_id=data_product_dataset.id,
                user_id=receiver,
            )
            db.add(notification)

    def create_data_output_dataset_notifications(
        self, db: Session, data_output_dataset: DataOutputDatasetAssociation
    ):
        receivers = set(
            owner.id
            for owner in (
                itertools.chain(
                    data_output_dataset.dataset.owners,
                    [data_output_dataset.requested_by],
                )
            )
        )
        for receiver in receivers:
            notification = DataOutputDatasetNotification(
                notification_type=NotificationTypes.DataOutputDatasetNotification,
                notification_origin=data_output_dataset.status,
                data_output_dataset_id=data_output_dataset.id,
                user_id=receiver,
            )
            db.add(notification)

    def create_data_product_membership_notifications(
        self, db: Session, data_product_membership: DataProductMembership
    ):
        receivers = set(
            owner.id
            for owner in (
                itertools.chain(
                    data_product_membership.data_product.owners,
                    [data_product_membership.user],
                )
            )
        )
        for receiver in receivers:
            notification = DataProductMembershipNotification(
                notification_type=NotificationTypes.DataProductMembershipNotification,
                notification_origin=data_product_membership.status,
                data_product_membership_id=data_product_membership.id,
                user_id=receiver,
            )
            db.add(notification)
