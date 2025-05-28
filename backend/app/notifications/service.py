from itertools import chain
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, desc, select
from sqlalchemy.orm import Session, joinedload

from app.notifications.model import Notification as NotificationModel
from app.notifications.schema_response import NotificationGet
from app.role_assignments.data_product.model import DataProductRoleAssignment
from app.role_assignments.dataset.model import DatasetRoleAssignment
from app.role_assignments.enums import DecisionStatus
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

        if not authenticated_user.is_admin and (
            notification.user_id != authenticated_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Notification does not belong to authenticated user",
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
        assignments = db.scalars(
            select(DatasetRoleAssignment).where(
                DatasetRoleAssignment.dataset_id == dataset_id,
                DatasetRoleAssignment.decision == DecisionStatus.APPROVED,
            )
        ).all()

        receivers = set(
            chain(
                (assignment.user_id for assignment in assignments),
                bonus_receiver_ids,
            )
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
        assignments = db.scalars(
            select(DataProductRoleAssignment).where(
                DataProductRoleAssignment.data_product_id == data_product_id,
                DataProductRoleAssignment.decision == DecisionStatus.APPROVED,
            )
        ).all()

        receivers = set(
            chain(
                (assignment.user_id for assignment in assignments),
                bonus_receiver_ids,
            )
        )
        for receiver in receivers:
            notification = NotificationModel(user_id=receiver, event_id=event_id)
            db.add(notification)
