from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.authz import Action
from app.database.database import ensure_exists
from app.events.enum import EventReferenceEntity, EventType
from app.events.model import Event as EventModel
from app.events.schema import CreateEvent
from app.events.service import EventService
from app.notifications.service import NotificationService
from app.role_assignments.dataset.model import DatasetRoleAssignment
from app.role_assignments.dataset.schema import (
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
        return ensure_exists(id_, self.db, DatasetRoleAssignment)

    def list_assignments(
        self,
        *,
        dataset_id: Optional[UUID],
        user_id: Optional[UUID],
        decision: Optional[DecisionStatus] = None,
    ) -> Sequence[RoleAssignment]:
        query = select(DatasetRoleAssignment)
        if dataset_id is not None:
            query = query.where(DatasetRoleAssignment.dataset_id == dataset_id)
        if user_id is not None:
            query = query.where(DatasetRoleAssignment.user_id == user_id)
        if decision is not None:
            query = query.where(DatasetRoleAssignment.decision == decision)

        return self.db.scalars(query).all()

    def create_assignment(
        self, dataset_id: UUID, request: CreateRoleAssignment, *, actor: User
    ) -> RoleAssignment:
        self.ensure_is_dataset_scope(request.role_id)
        existing_assignment = self.db.scalar(
            select(DatasetRoleAssignment).where(
                DatasetRoleAssignment.user_id == request.user_id,
                DatasetRoleAssignment.dataset_id == dataset_id,
            )
        )
        if existing_assignment:
            if existing_assignment.decision == DecisionStatus.DENIED:
                self.db.delete(existing_assignment)
                self.db.flush()
            else:
                detail = "Role assignment already exists for this user and dataset."
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=detail,
                )

        role_assignment = DatasetRoleAssignment(
            **request.model_dump(),
            dataset_id=dataset_id,
            requested_on=datetime.now(),
            requested_by_id=actor.id,
        )
        self.db.add(role_assignment)
        self.db.flush()
        self.db.add(
            EventModel(
                name=EventType.DATASET_ROLE_ASSIGNMENT_CREATED,
                subject_id=role_assignment.dataset_id,
                subject_type=EventReferenceEntity.DATASET,
                target_id=role_assignment.user_id,
                target_type=EventReferenceEntity.USER,
                actor_id=actor.id,
            )
        )
        self.db.commit()
        return role_assignment

    def delete_assignment(self, id_: UUID, *, actor: User) -> RoleAssignment:
        assignment = self.get_assignment(id_)
        self._guard_against_illegal_owner_removal(assignment)

        event_id = EventService(self.db).create_event(
            CreateEvent(
                name=EventType.DATASET_ROLE_ASSIGNMENT_REMOVED,
                subject_id=assignment.dataset_id,
                subject_type=EventReferenceEntity.DATASET,
                target_id=assignment.user_id,
                target_type=EventReferenceEntity.USER,
                actor_id=actor.id,
            ),
        )
        NotificationService(self.db).create_dataset_notifications(
            assignment.dataset_id,
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
        self, request: UpdateRoleAssignment, *, actor: User
    ) -> RoleAssignment:
        assignment = self.get_assignment(request.id)
        self._guard_against_illegal_owner_removal(assignment)

        if (role_id := request.role_id) is not None:
            self.ensure_is_dataset_scope(role_id)
            assignment.role_id = role_id
        if (decision := request.decision) is not None:
            assignment.decision = decision
            assignment.decided_on = datetime.now()
            assignment.decided_by_id = actor.id
            event_id = EventService(self.db).create_event(
                CreateEvent(
                    name=(
                        EventType.DATASET_ROLE_ASSIGNMENT_APPROVED
                        if assignment.decision == DecisionStatus.APPROVED
                        else EventType.DATASET_ROLE_ASSIGNMENT_DENIED
                    ),
                    subject_id=assignment.dataset_id,
                    subject_type=EventReferenceEntity.DATASET,
                    target_id=assignment.user_id,
                    target_type=EventReferenceEntity.USER,
                    actor_id=actor.id,
                ),
            )
            NotificationService(self.db).create_dataset_notifications(
                assignment.dataset_id,
                event_id,
                (
                    [assignment.requested_by_id]
                    if assignment.requested_by_id is not None
                    else []
                ),
            )
        else:
            event_id = EventService(self.db).create_event(
                CreateEvent(
                    name=EventType.DATASET_ROLE_ASSIGNMENT_UPDATED,
                    subject_id=assignment.dataset_id,
                    subject_type=EventReferenceEntity.DATASET,
                    target_id=assignment.user_id,
                    target_type=EventReferenceEntity.USER,
                    actor_id=actor.id,
                ),
            )
            NotificationService(self.db).create_dataset_notifications(
                assignment.dataset_id,
                event_id,
                (
                    [assignment.requested_by_id]
                    if assignment.requested_by_id is not None
                    else []
                ),
            )

        self.db.commit()
        return assignment

    def _guard_against_illegal_owner_removal(self, assignment: RoleAssignment) -> None:
        if (
            assignment.role is not None
            and assignment.role.prototype == Prototype.OWNER
            and assignment.decision == DecisionStatus.APPROVED
            and self._count_owners(assignment.dataset_id) <= 1
        ):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "A dataset must always be owned by at least one user",
            )

    def _count_owners(self, dataset_id: UUID) -> int:
        query = (
            select(func.count())
            .select_from(DatasetRoleAssignment)
            .where(DatasetRoleAssignment.dataset_id == dataset_id)
            .join(Role)
            .where(Role.prototype == Prototype.OWNER)
        )
        return self.db.scalar(query)

    def ensure_is_dataset_scope(self, role_id: UUID) -> None:
        role = self.db.get(Role, role_id)
        if role and role.scope != Scope.DATASET:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role not found for this scope",
            )

    def has_assignment(self, dataset_id: UUID, user: User) -> bool:
        assignments = self.list_assignments(
            dataset_id=dataset_id,
            user_id=user.id,
            decision=DecisionStatus.APPROVED,
        )
        return len(assignments) > 0

    def users_with_authz_action(
        self, dataset_id: UUID, action: Action
    ) -> Sequence[User]:
        return (
            self.db.scalars(
                select(UserModel)
                .join(
                    DatasetRoleAssignment,
                    DatasetRoleAssignment.user_id == UserModel.id,
                )
                .join(Role, DatasetRoleAssignment.role_id == Role.id)
                .where(
                    DatasetRoleAssignment.dataset_id == dataset_id,
                    DatasetRoleAssignment.decision == DecisionStatus.APPROVED,
                    Role.permissions.contains([action]),
                )
            )
            .unique()
            .all()
        )
