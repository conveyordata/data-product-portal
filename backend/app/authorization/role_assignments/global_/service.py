from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.global_.admin import is_user_admin
from app.authorization.role_assignments.global_.model import (
    GlobalRoleAssignment as GlobalRoleAssignmentModel,
)
from app.authorization.role_assignments.global_.schema import (
    GlobalRoleAssignment,
    RoleAssignmentRequest,
    UpdateGlobalRoleAssignment,
)
from app.authorization.roles.model import Role as RoleModel
from app.authorization.roles.schema import Prototype, Scope
from app.core.authz import Authorization
from app.database.database import ensure_exists
from app.shared.model import naive_utc_now, to_naive_utc
from app.users.model import User as UserModel
from app.users.schema import User


class RoleAssignmentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_assignment(self, id_: UUID) -> GlobalRoleAssignment:
        return ensure_exists(id_, self.db, GlobalRoleAssignmentModel)

    def list_assignments(
        self,
        *,
        identity_id: Optional[UUID] = None,
        role_id: Optional[UUID] = None,
        decision: Optional[DecisionStatus] = None,
        users_only: bool = False,
    ) -> Sequence[GlobalRoleAssignment]:
        query = select(GlobalRoleAssignmentModel)

        if identity_id is not None:
            query = query.where(GlobalRoleAssignmentModel.identity_id == identity_id)
        if role_id is not None:
            query = query.where(GlobalRoleAssignmentModel.role_id == role_id)
        if decision is not None:
            query = query.where(GlobalRoleAssignmentModel.decision == decision)
        if users_only:
            query = query.join(
                UserModel, UserModel.id == GlobalRoleAssignmentModel.identity_id
            )

        return self.db.scalars(query).all()

    def create_assignment(
        self, request: RoleAssignmentRequest, *, actor: User
    ) -> GlobalRoleAssignment:
        self.ensure_is_global_scope(request.role_id)
        self.ensure_is_not_admin(request.role_id)
        role_assignment = GlobalRoleAssignmentModel(
            identity_id=request.identity_id,
            role_id=request.role_id,
            requested_on=naive_utc_now(),
            requested_by_id=actor.id,
        )
        self.db.add(role_assignment)
        self.db.flush()
        return role_assignment

    def delete_assignment(self, id_: UUID) -> GlobalRoleAssignment:
        assignment = self.get_assignment(id_)

        self.db.delete(assignment)
        self.db.flush()
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
            assignment.decided_on = naive_utc_now()
            assignment.decided_by_id = actor.id

        self.db.flush()
        return assignment

    def ensure_can_decide(self, id_: UUID, decision: DecisionStatus) -> None:
        original = self.get_assignment(id_)
        if original.decision not in (DecisionStatus.PENDING, decision):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="This assignment was already decided",
            )

    def become_admin(self, user: UserModel, expiry: datetime) -> None:
        self.ensure_can_become_admin(user)
        if to_naive_utc(expiry) <= naive_utc_now():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Admin expiry must be in the future",
            )
        user.admin_expiry = expiry
        self.db.flush()
        self.sync_admin_role(user.id)

    def revoke_admin(self, user: UserModel) -> None:
        user.admin_expiry = None
        self.db.flush()
        self.sync_admin_role(user.id)

    def is_admin(self, user_id: UUID) -> bool:
        return bool(self.db.scalar(select(is_user_admin(user_id))))

    def sync_admin_role(self, user_id: UUID) -> None:
        authorizer = Authorization()
        if self.is_admin(user_id):
            authorizer.assign_admin_role(user_id=str(user_id))
        else:
            authorizer.revoke_admin_role(user_id=str(user_id))

    def ensure_can_become_admin(self, user: UserModel) -> None:
        if not user.can_become_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not allowed to elevate to admin",
            )

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
