from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from ..auth import ResourceAuthAssignment
from .schema import RoleAssignment


@dataclass
class DataProductAuthAssignment(ResourceAuthAssignment):

    def __init__(
        self, assignment: RoleAssignment, *, previous_role_id: Optional[UUID] = None
    ) -> None:
        role_id = self._assert_invariants(assignment, previous_role_id)

        super().__init__(
            role_id=role_id,
            user_id=assignment.user_id,
            resource_id=assignment.data_product_id,
            previous_role_id=previous_role_id,
        )
