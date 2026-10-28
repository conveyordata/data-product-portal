from itertools import chain
from typing import Iterable, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, desc, or_, select
from sqlalchemy.orm import Session, joinedload

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.abstract_data_product.input_ports.model import InputPort
from app.authorization.role_assignments.data_product.model import (
    DataProductRoleAssignment,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.model import (
    DatasetRoleAssignment,
)
from app.core.authz.authorization import Authorization
from app.data_products.output_ports.announcements.model import (
    Announcement as AnnouncementModel,
)
from app.data_products.output_ports.model import OutputPort as OutputPortModel
from app.events.enums import EventEntityType
from app.events.model import Event as EventModel
from app.explorations.model import Exploration
from app.groups.model import GroupMembership
from app.users.model import User as UserModel
from app.users.notifications.model import Notification as NotificationModel
from app.users.schema import User


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_notifications(self, user: User) -> Sequence[NotificationModel]:
        notifications = self.db.scalars(
            select(NotificationModel)
            .options(
                joinedload(NotificationModel.user),
                joinedload(NotificationModel.event),
            )
            .join(EventModel, EventModel.id == NotificationModel.event_id)
            .outerjoin(AnnouncementModel, AnnouncementModel.id == EventModel.target_id)
            .where(
                NotificationModel.user_id == user.id,
                or_(
                    EventModel.target_type != EventEntityType.ANNOUNCEMENT,
                    EventModel.target_type.is_(None),
                    AnnouncementModel.id.is_not(None),
                ),
            )
            .order_by(desc(NotificationModel.created_on))
        ).all()
        return [
            notification
            for notification in notifications
            if notification.event.target_type != EventEntityType.ANNOUNCEMENT
            or notification.event.output_port is not None
        ]

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

        self._notify(receivers, event_id)

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
        extra_user_ids = set(
            self.db.scalars(
                select(UserModel.id).where(UserModel.id.in_(extra_receiver_ids))
            )
        )
        receivers = self._data_product_member_ids([data_product_id]) | extra_user_ids

        self._notify(receivers, event_id)

    def create_consumer_notifications(
        self,
        *,
        consumer_id: UUID,
        event_id: UUID,
        extra_receiver_ids: Sequence[UUID] = (),
    ) -> None:
        exploration_owner_id = self.db.scalar(
            select(Exploration.owner_id).where(Exploration.id == consumer_id)
        )
        if exploration_owner_id:
            self._notify({exploration_owner_id, *extra_receiver_ids}, event_id)
        else:
            self.create_data_product_notifications(
                data_product_id=consumer_id,
                event_id=event_id,
                extra_receiver_ids=extra_receiver_ids,
            )

    def create_announcement_notifications(
        self, *, output_port_id: UUID, event_id: UUID
    ) -> None:
        consumer_ids = set(
            self.db.scalars(
                select(InputPort.consuming_abstract_data_product_id).where(
                    InputPort.output_port_id == output_port_id,
                    InputPort.status == InputPortStatus.APPROVED,
                )
            )
        )
        explorations = self.db.execute(
            select(Exploration.id, Exploration.owner_id).where(
                Exploration.id.in_(consumer_ids)
            )
        ).all()
        consuming_data_product_ids = consumer_ids - {id for id, _ in explorations}
        producing_data_product_id = self.db.scalar(
            select(OutputPortModel.data_product_id).where(
                OutputPortModel.id == output_port_id
            )
        )
        producing_team = self._data_product_member_ids(
            [producing_data_product_id]
        ) | set(
            self.db.scalars(
                select(DatasetRoleAssignment.user_id).where(
                    DatasetRoleAssignment.output_port_id == output_port_id,
                    DatasetRoleAssignment.decision == DecisionStatus.APPROVED,
                )
            )
        )
        receivers = {owner_id for _, owner_id in explorations} | (
            self._data_product_member_ids(consuming_data_product_ids)
        )
        self._notify(receivers - producing_team, event_id)

    def remove_announcement_notifications(self, announcement_id: UUID) -> None:
        self.db.execute(
            delete(NotificationModel).where(
                NotificationModel.event_id.in_(
                    select(EventModel.id).where(
                        EventModel.target_id == announcement_id,
                        EventModel.target_type == EventEntityType.ANNOUNCEMENT,
                    )
                )
            )
        )
        self.db.flush()

    def _notify(self, receivers: set[UUID], event_id: UUID) -> None:
        self.db.flush()
        event = self.db.get(EventModel, event_id)
        already_notified = set(
            self.db.scalars(
                select(NotificationModel.user_id).where(
                    NotificationModel.event_id == event_id
                )
            )
        )
        for receiver in receivers - already_notified - {event.actor_id}:
            self.db.add(NotificationModel(user_id=receiver, event_id=event_id))

    def _data_product_member_ids(self, data_product_ids: Iterable[UUID]) -> set[UUID]:
        direct_user_ids = (
            select(UserModel.id)
            .join(
                DataProductRoleAssignment,
                DataProductRoleAssignment.identity_id == UserModel.id,
            )
            .where(
                DataProductRoleAssignment.data_product_id.in_(data_product_ids),
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
                DataProductRoleAssignment.data_product_id.in_(data_product_ids),
                DataProductRoleAssignment.decision == DecisionStatus.APPROVED,
            )
        )
        return set(self.db.scalars(direct_user_ids.union(group_member_user_ids)))
