from itertools import chain
from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, desc, select
from sqlalchemy.orm import Session, joinedload

from app.authorization.role_assignments.data_product.model import (
    DataProductRoleAssignment,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.model import (
    DatasetRoleAssignment,
)
from app.core.authz.authorization import Authorization
from app.events.model import Event as EventModel
from app.explorations.model import Exploration
from app.groups.model import GroupMembership
from app.users.model import User as UserModel
from app.users.notifications.model import Notification as NotificationModel
from app.users.notifications.schema_response import NotificationGet
from app.users.schema import User


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_notifications(self, user: User) -> Sequence[NotificationGet]:
        return self.db.scalars(
            select(NotificationModel)
            .options(
                joinedload(NotificationModel.user),
                joinedload(NotificationModel.event),
            )
            .where(NotificationModel.user_id == user.id)
            .order_by(desc(NotificationModel.created_on))
        ).all()

    def remove_notification(self, id: UUID, user: User) -> None:
        notification = self.db.get(
            NotificationModel,
            id,
        )
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification {id} not found",
            )

        is_admin = Authorization().has_admin_role(user_id=str(user.id))
        is_owner = notification.user_id == user.id
        if not (is_admin or is_owner):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Notification does not belong to authenticated user",
            )

        self.db.delete(notification)
        self.db.flush()

    def remove_all_notifications(self, user: User) -> None:
        self.db.execute(
            delete(NotificationModel).where(NotificationModel.user_id == user.id)
        )
        self.db.flush()

    def create_dataset_notifications(
        self,
        *,
        dataset_id: UUID,
        event_id: UUID,
        extra_receiver_ids: Sequence[UUID] = (),
    ) -> None:
        assignments = self.db.scalars(
            select(DatasetRoleAssignment).where(
                DatasetRoleAssignment.output_port_id == dataset_id,
                DatasetRoleAssignment.decision == DecisionStatus.APPROVED,
            )
        ).all()

        receivers = set(
            chain(
                (assignment.user_id for assignment in assignments),
                extra_receiver_ids,
            )
        )

        event = self.db.get(EventModel, event_id)
        for receiver in receivers:
            if receiver != event.actor_id:
                notification = NotificationModel(user_id=receiver, event_id=event_id)
                self.db.add(notification)

    def create_data_product_notifications(
        self,
        *,
        data_product_id: UUID,
        event_id: UUID,
        extra_receiver_ids: Sequence[UUID] = (),
    ) -> None:
        """
        Creates notifications for users related to a data product event.

        As approved Data Product assignments can target machine users and groups,
        those need to be excluded while including group members when the target is a group.

        `extra_receiver_ids` paraam is also filtered out to allow only users.
        """
        direct_user_ids = (
            select(UserModel.id)
            .join(
                DataProductRoleAssignment,
                DataProductRoleAssignment.identity_id == UserModel.id,
            )
            .where(
                DataProductRoleAssignment.data_product_id == data_product_id,
                DataProductRoleAssignment.decision == DecisionStatus.APPROVED,
            )
        )

        group_member_user_ids = (
            select(UserModel.id)
            .join(
                GroupMembership,
                GroupMembership.member_identity_id == UserModel.id,
            )
            .join(
                DataProductRoleAssignment,
                DataProductRoleAssignment.identity_id == GroupMembership.group_id,
            )
            .where(
                DataProductRoleAssignment.data_product_id == data_product_id,
                DataProductRoleAssignment.decision == DecisionStatus.APPROVED,
            )
        )

        extra_user_ids = select(UserModel.id).where(
            UserModel.id.in_(extra_receiver_ids)
        )

        receivers = set(
            self.db.scalars(
                direct_user_ids.union(
                    group_member_user_ids,
                    extra_user_ids,
                )
            ).all()
        )

        event = self.db.get(EventModel, event_id)
        for receiver in receivers:
            if receiver != event.actor_id:
                notification = NotificationModel(user_id=receiver, event_id=event_id)
                self.db.add(notification)

    def create_exploration_notifications(
        self,
        *,
        exploration_id: UUID,
        event_id: UUID,
    ) -> None:
        owner_id = self.db.scalar(
            select(Exploration.owner_id).where(Exploration.id == exploration_id)
        )
        if owner_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exploration {exploration_id} not found",
            )

        event = self.db.get(EventModel, event_id)
        if owner_id != event.actor_id:
            self.db.add(NotificationModel(user_id=owner_id, event_id=event_id))
