from typing import Optional

from ..auth import (
    ResourceAuthAssignment,
)
from .schema import RoleAssignment


class DatasetAuthAssignment(ResourceAuthAssignment):

    def __init__(
        self, assignment: RoleAssignment, *, previous: Optional[RoleAssignment] = None
    ):
        role_id = self._assert_invariants(assignment)

        super().__init__(
            role_id=role_id,
            user_id=assignment.user_id,
            resource_id=assignment.dataset_id,
            previous_role_id=previous.id if previous else None,
        )
