from dataclasses import dataclass
from typing import Optional, Union
from uuid import UUID

from app.core.authz.authorization import Authorization
from app.role_assignments.data_product.schema import (
    RoleAssignment as DataProductRoleAssignment,
)
from app.role_assignments.dataset.schema import RoleAssignment as DatasetRoleAssignment
from app.role_assignments.enums import DecisionStatus


@dataclass
class ResourceAuthAssignment:
    """Dataclass to pass values separate from the DB session."""

    resource_id: UUID
    user_id: UUID
    role_id: UUID
    previous_role_id: Optional[UUID] = None

    def with_previous(self, role_id: UUID) -> "ResourceAuthAssignment":
        self.previous_role_id = role_id
        return self

    @classmethod
    def _assert_invariants(
        cls, assignment: Union[DataProductRoleAssignment, DatasetRoleAssignment]
    ) -> UUID:
        assert (
            assignment.decision is DecisionStatus.APPROVED
        ), "Only approved decisions can be propagated to the enforcer"
        assert (
            assignment.role_id is not None
        ), "Only decisions that define a role can be propagated to the enforcer"

        return assignment.role_id


async def add_assignment(assignment: ResourceAuthAssignment) -> None:
    authorizer = Authorization()
    await authorizer.assign_resource_role(
        user_id=str(assignment.user_id),
        role_id=str(assignment.role_id),
        resource_id=str(assignment.resource_id),
    )


async def remove_assignment(assignment: ResourceAuthAssignment) -> None:
    authorizer = Authorization()
    await authorizer.revoke_resource_role(
        user_id=str(assignment.user_id),
        role_id=str(assignment.role_id),
        resource_id=str(assignment.resource_id),
    )


async def swap_assignment(assignment: ResourceAuthAssignment) -> None:
    assert assignment.previous_role_id is not None

    authorizer = Authorization()

    await authorizer.revoke_resource_role(
        user_id=str(assignment.user_id),
        role_id=str(assignment.previous_role_id),
        resource_id=str(assignment.resource_id),
    )

    await authorizer.assign_resource_role(
        user_id=str(assignment.user_id),
        role_id=str(assignment.role_id),
        resource_id=str(assignment.resource_id),
    )
