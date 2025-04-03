from dataclasses import dataclass

from ..tasks import (
    ResourceAuthAssignment,
    add_assignment,
    remove_assignment,
    swap_assignment,
)
from .schema import RoleAssignment


@dataclass
class AuthAssignment(ResourceAuthAssignment):
    @classmethod
    def from_data_product(cls, assignment: RoleAssignment) -> "ResourceAuthAssignment":
        role_id = cls._assert_invariants(assignment)

        return ResourceAuthAssignment(
            role_id=role_id,
            user_id=assignment.user_id,
            resource_id=assignment.data_product_id,
        )


__all__ = ["AuthAssignment", "add_assignment", "remove_assignment", "swap_assignment"]
