from dataclasses import dataclass
from typing import Optional

from ..auth import ResourceAuthAssignment
from .schema import RoleAssignment


@dataclass
class DataProductAuthAssignment(ResourceAuthAssignment):

    def __init__(
        self, assignment: RoleAssignment, *, previous: Optional[RoleAssignment] = None
    ) -> None:
        role_id = self._assert_invariants(assignment)

        super().__init__(
            role_id=role_id,
            user_id=assignment.user_id,
            resource_id=assignment.data_product_id,
            previous_role_id=previous.role_id if previous else None,
        )
