from itertools import chain
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, desc, select
from sqlalchemy.orm import Session, joinedload

from app.core.authz.authorization import Authorization
from app.notifications.model import Notification as NotificationModel
from app.notifications.schema_response import NotificationGet
from app.role_assignments.data_product.model import DataProductRoleAssignment
from app.role_assignments.dataset.model import DatasetRoleAssignment
from app.role_assignments.enums import DecisionStatus
from app.users.schema import User


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_notifications(self, authenticated_user: User) -> list[NotificationGet]:
        return self.db.scalars(
            select(NotificationModel)
            .options(
                joinedload(NotificationModel.user),
                joinedload(NotificationModel.event),
            )
            .where(NotificationModel.user_id == authenticated_user.id)
            .order_by(desc(NotificationModel.created_on))
        ).all()

    def remove_notification(self, id: UUID, authenticated_user: User) -> None:
        notification = self.db.get(
            NotificationModel,
            id,
        )
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification {id} not found",
            )

        auth = Authorization()
        is_admin = auth.has_admin_role(user_id=str(authenticated_user.id))
        is_owner = notification.user_id == authenticated_user.id
        if not is_admin and not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Notification does not belong to authenticated user",
            )
        self.db.delete(notification)
        self.db.commit()

    def remove_all_notifications(self, authenticated_user: User) -> None:
        self.db.execute(
            delete(NotificationModel).where(
                NotificationModel.user_id == authenticated_user.id
            )
        )
        self.db.commit()

    def create_dataset_notifications(
        self,
        dataset_id: UUID,
        event_id: UUID,
        bonus_receiver_ids: list[UUID] = [],
    ) -> None:
        assignments = self.db.scalars(
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
            self.db.add(notification)

    def create_data_product_notifications(
        self,
        data_product_id: UUID,
        event_id: UUID,
        bonus_receiver_ids: list[UUID] = [],
    ) -> None:
        assignments = self.db.scalars(
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
            self.db.add(notification)
