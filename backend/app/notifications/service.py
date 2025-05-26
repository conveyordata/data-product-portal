from itertools import chain
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, desc, select
from sqlalchemy.orm import Session, joinedload

from app.data_products.model import ensure_data_product_exists
from app.datasets.model import ensure_dataset_exists
from app.notifications.model import Notification as NotificationModel
from app.notifications.schema_response import NotificationGet
from app.users.schema import User


class NotificationService:
    def get_user_notifications(
        self, db: Session, authenticated_user: User
    ) -> list[NotificationGet]:
        return db.scalars(
            select(NotificationModel)
            .options(
                joinedload(NotificationModel.user),
                joinedload(NotificationModel.event),
            )
            .where(NotificationModel.user_id == authenticated_user.id)
            .order_by(desc(NotificationModel.created_on))
        ).all()

    def remove_notification(
        self, id: UUID, db: Session, authenticated_user: User
    ) -> None:
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

    def remove_all_notifications(self, db: Session, authenticated_user: User) -> None:
        db.execute(
            delete(NotificationModel).where(
                NotificationModel.user_id == authenticated_user.id
            )
        )
        db.commit()

    def create_dataset_notifications(
        self,
        db: Session,
        dataset_id: UUID,
        event_id: UUID,
        bonus_receiver_ids: list[UUID] = [],
    ) -> None:
        dataset = ensure_dataset_exists(dataset_id, db)
        receivers = set(
            chain((owner.id for owner in dataset.owners), bonus_receiver_ids)
        )
        for receiver in receivers:
            notification = NotificationModel(user_id=receiver, event_id=event_id)
            db.add(notification)

    def create_data_product_notifications(
        self,
        db: Session,
        data_product_id: UUID,
        event_id: UUID,
        bonus_receiver_ids: list[UUID] = [],
    ) -> None:
        data_product = ensure_data_product_exists(data_product_id, db)
        receivers = set(
            chain(
                (assignment.user_id for assignment in data_product.assignments),
                bonus_receiver_ids,
            )
        )
        for receiver in receivers:
            notification = NotificationModel(user_id=receiver, event_id=event_id)
            db.add(notification)
