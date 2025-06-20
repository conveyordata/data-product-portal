from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import ensure_exists
from app.role_assignments.enums import DecisionStatus
from app.role_assignments.global_.model import GlobalRoleAssignment
from app.role_assignments.global_.schema import (
    RoleAssignment,
    RoleAssignmentRequest,
    UpdateRoleAssignment,
)
from app.roles.model import Role
from app.roles.schema import Scope
from app.users.schema import User


class RoleAssignmentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_assignment(self, id_: UUID) -> RoleAssignment:
        return ensure_exists(id_, self.db, GlobalRoleAssignment)

    def list_assignments(
        self, *, user_id: Optional[UUID], decision: Optional[DecisionStatus] = None
    ) -> Sequence[RoleAssignment]:
        query = select(GlobalRoleAssignment)
        if user_id is not None:
            query = query.where(GlobalRoleAssignment.user_id == user_id)
        if decision is not None:
            query = query.where(GlobalRoleAssignment.decision == decision)

        return self.db.scalars(query).all()

    def create_assignment(
        self, request: RoleAssignmentRequest, *, actor: User
    ) -> RoleAssignment:
        self.ensure_is_global_scope(request.role_id)
        role_assignment = GlobalRoleAssignment(
            **request.model_dump(),
            requested_on=datetime.now(),
            requested_by_id=actor.id,
        )
        self.db.add(role_assignment)
        self.db.commit()
        return role_assignment

    def delete_assignment(self, id_: UUID) -> RoleAssignment:
        assignment = self.get_assignment(id_)
        self.db.delete(assignment)
        self.db.commit()
        return assignment

    def ensure_is_global_scope(self, role_id: UUID) -> None:
        role = self.db.get(Role, role_id)
        if role and role.scope != Scope.GLOBAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role not found for this scope",
            )

    def update_assignment(
        self, request: UpdateRoleAssignment, *, actor: User
    ) -> RoleAssignment:
        assignment = self.get_assignment(request.id)

        if (role_id := request.role_id) is not None:
            self.ensure_is_global_scope(role_id)
            assignment.role_id = role_id
        if (decision := request.decision) is not None:
            assignment.decision = decision
            assignment.decided_on = datetime.now()
            assignment.decided_by_id = actor.id

        self.db.commit()
        return assignment
