from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.authorization.role_assignments.auth import ResourceAuthAssignment

from .schema import DataProductRoleAssignment


@dataclass
class DataProductAuthAssignment(ResourceAuthAssignment):
    def __init__(
        self,
        assignment: DataProductRoleAssignment,
        *,
        previous_role_id: Optional[UUID] = None,
    ) -> None:
        role_id = self._assert_invariants(assignment, previous_role_id)

        super().__init__(
            role_id=role_id,
            # TODO moving user_id to identity_id is a breaking change for the webhook so let's do it later on
            user_id=assignment.identity_id,
            resource_id=assignment.data_product_id,
            previous_role_id=previous_role_id,
        )
