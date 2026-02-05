from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.global_.model import GlobalRoleAssignmentModel
from app.authorization.role_assignments.global_.schema import (
    GlobalRoleAssignment,
    RoleAssignmentRequest,
    UpdateGlobalRoleAssignment,
)
from app.authorization.roles.model import Role as RoleModel
from app.authorization.roles.schema import Prototype, Scope
from app.database.database import ensure_exists
from app.users.schema import User


class RoleAssignmentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_assignment(self, id_: UUID) -> GlobalRoleAssignment:
        return ensure_exists(id_, self.db, GlobalRoleAssignmentModel)

    def list_assignments(
        self,
        *,
        user_id: Optional[UUID] = None,
        role_id: Optional[UUID] = None,
        decision: Optional[DecisionStatus] = None,
    ) -> Sequence[GlobalRoleAssignment]:
        query = select(GlobalRoleAssignmentModel)
        if user_id is not None:
            query = query.where(GlobalRoleAssignmentModel.user_id == user_id)
        if role_id is not None:
            query = query.where(GlobalRoleAssignmentModel.role_id == role_id)
        if decision is not None:
            query = query.where(GlobalRoleAssignmentModel.decision == decision)

        return self.db.scalars(query).all()

    def create_assignment(
        self, request: RoleAssignmentRequest, *, actor: User
    ) -> GlobalRoleAssignment:
        self.ensure_is_global_scope(request.role_id)
        self.ensure_is_not_admin(request.role_id)
        role_assignment = GlobalRoleAssignmentModel(
            **request.model_dump(),
            requested_on=datetime.now(),
            requested_by_id=actor.id,
        )
        self.db.add(role_assignment)
        self.db.commit()
        return role_assignment

    def delete_assignment(self, id_: UUID) -> GlobalRoleAssignment:
        assignment = self.get_assignment(id_)

        self.db.delete(assignment)
        self.db.commit()
        return assignment

    def update_assignment(
        self, request: UpdateGlobalRoleAssignment, *, actor: User
    ) -> GlobalRoleAssignment:
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

    def ensure_is_global_scope(self, role_id: UUID) -> None:
        role = self.db.get(RoleModel, role_id)
        if role and role.scope != Scope.GLOBAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role not found for this scope",
            )

    def ensure_is_not_admin(self, role_id: UUID) -> None:
        role = self.db.get(RoleModel, role_id)
        if role and role.prototype == Prototype.ADMIN:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Admin role assignments are no longer allowed",
            )
