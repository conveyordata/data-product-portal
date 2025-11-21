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
    def add(self) -> bool: ...

    def remove(self) -> bool: ...

    def swap(self) -> tuple[bool, bool]: ...


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
        if assignment.decision is not DecisionStatus.APPROVED:
            raise Exception("Only approved decisions can be propagated to the enforcer")
        if assignment.role_id is None:
            raise Exception(
                "Only decisions that define a role can be propagated to the enforcer"
            )
        if assignment.role_id == previous_role_id:
            raise Exception(
                "Re-assigning the same role is a no-op and indicates a logic bug"
            )

        return assignment.role_id

    def add(self) -> bool:
        authorizer = Authorization()
        return authorizer.assign_resource_role(
            user_id=str(self.user_id),
            role_id=str(self.role_id),
            resource_id=str(self.resource_id),
        )

    def remove(self) -> bool:
        authorizer = Authorization()
        return authorizer.revoke_resource_role(
            user_id=str(self.user_id),
            role_id=str(self.role_id),
            resource_id=str(self.resource_id),
        )

    def swap(self) -> tuple[bool, bool]:
        if self.previous_role_id is None:
            raise ValueError("Cannot swap roles without a previous role")

        authorizer = Authorization()
        revoke = authorizer.revoke_resource_role(
            user_id=str(self.user_id),
            role_id=str(self.previous_role_id),
            resource_id=str(self.resource_id),
        )
        assign = authorizer.assign_resource_role(
            user_id=str(self.user_id),
            role_id=str(self.role_id),
            resource_id=str(self.resource_id),
        )
        return revoke, assign
