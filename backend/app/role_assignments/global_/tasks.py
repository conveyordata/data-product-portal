from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.core.authz.authorization import Authorization
from app.roles.service import ADMIN_UUID

from .schema import RoleAssignment


@dataclass
class AuthAssignment:
    """Dataclass to pass values separate from the DB session."""

    user_id: UUID
    role_id: UUID
    previous_role_id: Optional[UUID] = None

    @classmethod
    def from_global(cls, assignment: RoleAssignment) -> "AuthAssignment":
        return cls(
            user_id=assignment.user_id,
            role_id=assignment.role_id,
        )

    def with_previous(self, role_id: UUID) -> "AuthAssignment":
        self.previous_role_id = role_id
        return self

    def is_admin(self) -> bool:
        return self.role_id == ADMIN_UUID

    def was_admin(self) -> bool:
        return self.previous_role_id == ADMIN_UUID


async def add_assignment(assignment: AuthAssignment) -> None:
    authorizer = Authorization()

    if assignment.is_admin():
        await authorizer.assign_admin_role(user_id=str(assignment.user_id))
    else:
        await authorizer.assign_global_role(
            user_id=str(assignment.user_id),
            role_id=str(assignment.role_id),
        )


async def remove_assignment(assignment: AuthAssignment) -> None:
    authorizer = Authorization()
    if assignment.is_admin():
        await authorizer.revoke_admin_role(user_id=str(assignment.user_id))
    else:
        await authorizer.revoke_global_role(
            user_id=str(assignment.user_id),
            role_id=str(assignment.role_id),
        )


async def swap_assignment(assignment: AuthAssignment) -> None:
    assert assignment.previous_role_id is not None

    authorizer = Authorization()

    if assignment.was_admin():
        await authorizer.revoke_admin_role(user_id=str(assignment.user_id))
    else:
        await authorizer.revoke_global_role(
            user_id=str(assignment.user_id),
            role_id=str(assignment.previous_role_id),
        )

    if assignment.is_admin():
        await authorizer.assign_admin_role(user_id=str(assignment.user_id))
    else:
        await authorizer.assign_global_role(
            user_id=str(assignment.user_id),
            role_id=str(assignment.role_id),
        )
