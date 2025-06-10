from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import asc, func, select
from sqlalchemy.orm import Session

from app.core.authz import Action
from app.database.database import ensure_exists
from app.events.enum import EventReferenceEntity, EventType
from app.events.model import Event as EventModel
from app.events.schema import CreateEvent
from app.events.service import EventService
from app.notifications.service import NotificationService
from app.pending_actions.schema import DataProductRoleAssignmentPendingAction
from app.role_assignments.data_product.model import DataProductRoleAssignment
from app.role_assignments.data_product.schema import (
    CreateRoleAssignment,
    RoleAssignment,
    UpdateRoleAssignment,
)
from app.role_assignments.enums import DecisionStatus
from app.roles.model import Role
from app.roles.schema import Prototype, Scope
from app.users.model import User as UserModel
from app.users.schema import User


class RoleAssignmentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_assignment(self, id_: UUID) -> RoleAssignment:
        return ensure_exists(id_, self.db, DataProductRoleAssignment)

    def list_assignments(
        self,
        *,
        data_product_id: Optional[UUID],
        user_id: Optional[UUID],
        decision: Optional[DecisionStatus] = None,
    ) -> Sequence[RoleAssignment]:
        query = select(DataProductRoleAssignment)
        if data_product_id is not None:
            query = query.where(
                DataProductRoleAssignment.data_product_id == data_product_id
            )
        if user_id is not None:
            query = query.where(DataProductRoleAssignment.user_id == user_id)
        if decision is not None:
            query = query.where(DataProductRoleAssignment.decision == decision)

        return self.db.scalars(query).all()

    def create_assignment(
        self, data_product_id: UUID, request: CreateRoleAssignment, actor: User
    ) -> RoleAssignment:
        self.ensure_is_data_product_scope(request.role_id)
        existing_assignment = self.db.scalar(
            select(DataProductRoleAssignment).where(
                DataProductRoleAssignment.user_id == request.user_id,
                DataProductRoleAssignment.data_product_id == data_product_id,
            )
        )
        if existing_assignment:
            if existing_assignment.decision == DecisionStatus.DENIED:
                self.db.delete(existing_assignment)
                self.db.flush()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Role assignment already"
                        " exists for"
                        " this user and data product."
                    ),
                )

        role_assignment = DataProductRoleAssignment(
            **request.model_dump(),
            data_product_id=data_product_id,
            requested_on=datetime.now(),
            requested_by_id=actor.id,
        )
        self.db.add(role_assignment)
        self.db.flush()
        self.db.add(
            EventModel(
                name=EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_CREATED,
                subject_id=role_assignment.data_product_id,
                subject_type=EventReferenceEntity.DATA_PRODUCT,
                target_id=role_assignment.user_id,
                target_type=EventReferenceEntity.USER,
                actor_id=actor.id,
            )
        )
        self.db.commit()
        return role_assignment

    def delete_assignment(self, id_: UUID, authenticated_user: User) -> RoleAssignment:
        assignment = self.get_assignment(id_)
        self._guard_against_illegal_owner_removal(assignment)

        event_id = EventService().create_event(
            self.db,
            CreateEvent(
                name=EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_REMOVED,
                subject_id=assignment.data_product_id,
                subject_type=EventReferenceEntity.DATA_PRODUCT,
                target_id=assignment.user_id,
                target_type=EventReferenceEntity.USER,
                actor_id=authenticated_user.id,
            ),
        )
        NotificationService(self.db).create_data_product_notifications(
            assignment.data_product_id,
            event_id,
            (
                [assignment.requested_by_id]
                if assignment.requested_by_id is not None
                else []
            ),
        )
        self.db.delete(assignment)
        self.db.commit()
        return assignment

    def update_assignment(
        self, request: UpdateRoleAssignment, actor: User
    ) -> RoleAssignment:
        assignment = self.get_assignment(request.id)
        self._guard_against_illegal_owner_removal(assignment)

        if (role_id := request.role_id) is not None:
            self.ensure_is_data_product_scope(role_id)
            assignment.role_id = role_id
        if (decision := request.decision) is not None:
            assignment.decision = decision
            assignment.decided_on = datetime.now()
            assignment.decided_by_id = actor.id

            event_id = EventService().create_event(
                self.db,
                CreateEvent(
                    name=(
                        EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_APPROVED
                        if assignment.decision == DecisionStatus.APPROVED
                        else EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_DENIED
                    ),
                    subject_id=assignment.data_product_id,
                    subject_type=EventReferenceEntity.DATA_PRODUCT,
                    target_id=assignment.user_id,
                    target_type=EventReferenceEntity.USER,
                    actor_id=actor.id,
                ),
            )
            NotificationService(self.db).create_data_product_notifications(
                assignment.data_product_id,
                event_id,
                (
                    [assignment.requested_by_id]
                    if assignment.requested_by_id is not None
                    else []
                ),
            )
        else:
            event_id = EventService().create_event(
                self.db,
                CreateEvent(
                    name=EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_UPDATED,
                    subject_id=assignment.data_product_id,
                    subject_type=EventReferenceEntity.DATA_PRODUCT,
                    target_id=assignment.user_id,
                    target_type=EventReferenceEntity.USER,
                    actor_id=actor.id,
                ),
            )
            NotificationService(self.db).create_data_product_notifications(
                assignment.data_product_id,
                event_id,
                (
                    [assignment.requested_by_id]
                    if assignment.requested_by_id is not None
                    else []
                ),
            )
        self.db.commit()
        return assignment

    def ensure_is_data_product_scope(self, role_id: UUID) -> None:
        role = self.db.get(Role, role_id)
        if role and role.scope != Scope.DATA_PRODUCT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role not found for this scope",
            )

    def _guard_against_illegal_owner_removal(self, assignment: RoleAssignment) -> None:
        if (
            assignment.role is not None
            and assignment.role.prototype == Prototype.OWNER
            and assignment.decision == DecisionStatus.APPROVED
            and self._count_owners(assignment.data_product_id) <= 1
        ):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "A data product must always be owned by at least one user",
            )

    def _count_owners(self, data_product_id: UUID) -> int:
        query = (
            select(func.count())
            .select_from(DataProductRoleAssignment)
            .where(DataProductRoleAssignment.data_product_id == data_product_id)
            .join(Role)
            .where(Role.prototype == Prototype.OWNER)
        )
        return self.db.scalar(query)

    def get_pending_data_product_role_assignments(
        self, user: User
    ) -> Sequence[DataProductRoleAssignmentPendingAction]:
        data_product_ids = (
            select(DataProductRoleAssignment.data_product_id)
            .join(DataProductRoleAssignment.role)
            .where(
                DataProductRoleAssignment.user_id == user.id,
                DataProductRoleAssignment.decision == DecisionStatus.APPROVED,
                Role.permissions.contains(
                    [Action.DATA_PRODUCT__APPROVE_USER_REQUEST.value]
                ),
            )
            .scalar_subquery()
        )

        actions = (
            self.db.scalars(
                select(DataProductRoleAssignment)
                .filter(DataProductRoleAssignment.decision == DecisionStatus.PENDING)
                .filter(DataProductRoleAssignment.data_product_id.in_(data_product_ids))
                .order_by(asc(DataProductRoleAssignment.requested_on))
            )
            .unique()
            .all()
        )
        return actions

    def users_with_authz_action(
        self, data_product_id: UUID, action: Action
    ) -> Sequence[User]:
        return (
            self.db.scalars(
                select(UserModel)
                .join(
                    DataProductRoleAssignment,
                    DataProductRoleAssignment.user_id == UserModel.id,
                )
                .join(Role, DataProductRoleAssignment.role_id == Role.id)
                .where(
                    DataProductRoleAssignment.data_product_id == data_product_id,
                    DataProductRoleAssignment.decision == DecisionStatus.APPROVED,
                    Role.permissions.contains([action]),
                )
            )
            .unique()
            .all()
        )
