from dataclasses import dataclass
from typing import Optional, Protocol, Union
from uuid import UUID

from app.core.authz.authorization import Authorization
from app.role_assignments.data_product.schema import (
    RoleAssignment as DataProductRoleAssignment,
)
from app.role_assignments.dataset.schema import RoleAssignment as DatasetRoleAssignment
from app.role_assignments.enums import DecisionStatus


class AuthAssignment(Protocol):
    async def add(self) -> None: ...

    async def remove(self) -> None: ...

    async def swap(self) -> None: ...


@dataclass
class ResourceAuthAssignment(AuthAssignment):
    """Dataclass to pass values separate from the DB session."""

    resource_id: UUID
    user_id: UUID
    role_id: UUID
    previous_role_id: Optional[UUID] = None

    @classmethod
    def _assert_invariants(
        cls,
        assignment: Union[DataProductRoleAssignment, DatasetRoleAssignment],
        previous_role_id: Optional[UUID],
    ) -> UUID:
        assert (
            assignment.decision is DecisionStatus.APPROVED
        ), "Only approved decisions can be propagated to the enforcer"
        assert (
            assignment.role_id is not None
        ), "Only decisions that define a role can be propagated to the enforcer"
        assert (
            assignment.role_id != previous_role_id
        ), "Re-assigning the same role is a no-op and indicates a logic bug"

        return assignment.role_id

    async def add(self) -> None:
        authorizer = Authorization()
        await authorizer.assign_resource_role(
            user_id=str(self.user_id),
            role_id=str(self.role_id),
            resource_id=str(self.resource_id),
        )

    async def remove(self) -> None:
        authorizer = Authorization()
        await authorizer.revoke_resource_role(
            user_id=str(self.user_id),
            role_id=str(self.role_id),
            resource_id=str(self.resource_id),
        )

    async def swap(self) -> None:
        assert self.previous_role_id is not None

        authorizer = Authorization()
        await authorizer.revoke_resource_role(
            user_id=str(self.user_id),
            role_id=str(self.previous_role_id),
            resource_id=str(self.resource_id),
        )
        await authorizer.assign_resource_role(
            user_id=str(self.user_id),
            role_id=str(self.role_id),
            resource_id=str(self.resource_id),
        )
