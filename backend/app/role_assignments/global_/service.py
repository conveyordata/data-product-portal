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
from app.roles.model import Role as RoleModel
from app.roles.schema import Prototype, Scope
from app.users.schema import User


class RoleAssignmentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_assignment(self, id_: UUID) -> RoleAssignment:
        return ensure_exists(id_, self.db, GlobalRoleAssignment)

    def list_assignments(
        self,
        *,
        user_id: Optional[UUID] = None,
        role_id: Optional[UUID] = None,
        decision: Optional[DecisionStatus] = None,
    ) -> Sequence[RoleAssignment]:
        query = select(GlobalRoleAssignment)
        if user_id is not None:
            query = query.where(GlobalRoleAssignment.user_id == user_id)
        if role_id is not None:
            query = query.where(GlobalRoleAssignment.role_id == role_id)
        if decision is not None:
            query = query.where(GlobalRoleAssignment.decision == decision)

        return self.db.scalars(query).all()

    def create_assignment(
        self, request: RoleAssignmentRequest, *, actor: User
    ) -> RoleAssignment:
        self.ensure_is_global_scope(request.role_id)
        self.ensure_admin_has_expiry(request.role_id, request.expiry)
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
        # self._guard_against_illegal_admin_removal(assignment)

        self.db.delete(assignment)
        self.db.commit()
        return assignment

    def update_assignment(
        self, request: UpdateRoleAssignment, *, actor: User
    ) -> RoleAssignment:
        assignment = self.get_assignment(request.id)
        # self._guard_against_illegal_admin_removal(assignment)

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

    def ensure_admin_has_expiry(
        self, role_id: UUID, expiry: Optional[datetime]
    ) -> None:
        role = self.db.get(RoleModel, role_id)
        if role and role.prototype == Prototype.ADMIN and expiry is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Admin role assignments must have an expiry date",
            )

    # def _guard_against_illegal_admin_
    # removal(self, assignment: RoleAssignment) -> None:
    #     # TODO Check that at least 1 user has the become admin thingy
    #     pass
    #     # if (
    #     #     assignment.role is not None
    #     #     and assignment.role.prototype == Prototype.PRE_ADMIN
    #     #     and assignment.decision == DecisionStatus.APPROVED
    #     #     and self._count_admins() <= 1
    #     # ):
    #     #     raise HTTPException(
    #     #         status.HTTP_403_FORBIDDEN,
    #     #         "At least one user need to have elevate to admin",
    #     #     )

    # def _count_admins(self) -> int:
    #     query = (
    #         select(func.count())
    #         .select_from(GlobalRoleAssignment)
    #         .join(GlobalRoleAssignment.user)
    #         .where(UserModel.email != SYSTEM_ACCOUNT)
    #         .join(GlobalRoleAssignment.role)
    #     )
    #     return self.db.scalar(query)
