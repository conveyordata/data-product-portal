from ..tasks import (
    ResourceAuthAssignment,
    add_assignment,
    remove_assignment,
    swap_assignment,
)
from .schema import RoleAssignment


class AuthAssignment(ResourceAuthAssignment):
    @classmethod
    def from_dataset(cls, assignment: RoleAssignment) -> "AuthAssignment":
        role_id = cls._assert_invariants(assignment)

        return cls(
            role_id=role_id,
            user_id=assignment.user_id,
            resource_id=assignment.dataset_id,
        )


__all__ = ["AuthAssignment", "add_assignment", "remove_assignment", "swap_assignment"]
