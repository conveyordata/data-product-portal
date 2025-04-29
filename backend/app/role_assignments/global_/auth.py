from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.core.authz.authorization import Authorization
from app.roles import ADMIN_UUID

from ..auth import AuthAssignment
from .schema import RoleAssignment


@dataclass
class _GlobalAuthAssignment(AuthAssignment):
    user_id: UUID
    role_id: UUID
    previous_role_id: Optional[UUID] = None


class GlobalAuthAssignment(_GlobalAuthAssignment):
    """Dataclass to pass values separate from the DB session."""

    def __init__(
        self, assignment: RoleAssignment, *, previous: Optional[RoleAssignment] = None
    ) -> None:
        super().__init__(
            user_id=assignment.user_id,
            role_id=assignment.role_id,
            previous_role_id=previous.role_id if previous else None,
        )

    def is_admin(self) -> bool:
        return self.role_id == ADMIN_UUID

    def was_admin(self) -> bool:
        return self.previous_role_id == ADMIN_UUID

    async def add(self) -> None:
        authorizer = Authorization()

        if self.is_admin():
            await authorizer.assign_admin_role(user_id=str(self.user_id))
        else:
            await authorizer.assign_global_role(
                user_id=str(self.user_id),
                role_id=str(self.role_id),
            )

    async def remove(self) -> None:
        authorizer = Authorization()
        if self.is_admin():
            await authorizer.revoke_admin_role(user_id=str(self.user_id))
        else:
            await authorizer.revoke_global_role(
                user_id=str(self.user_id),
                role_id=str(self.role_id),
            )

    async def swap(self) -> None:
        assert self.previous_role_id is not None

        authorizer = Authorization()

        if self.was_admin():
            await authorizer.revoke_admin_role(user_id=str(self.user_id))
        else:
            await authorizer.revoke_global_role(
                user_id=str(self.user_id),
                role_id=str(self.previous_role_id),
            )

        if self.is_admin():
            await authorizer.assign_admin_role(user_id=str(self.user_id))
        else:
            await authorizer.assign_global_role(
                user_id=str(self.user_id),
                role_id=str(self.role_id),
            )
