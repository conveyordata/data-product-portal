from enum import Enum


class AssignmentFilter(str, Enum):
    ALL = "all"
    ONLY_ASSIGNED = "only_assigned"

    def __str__(self) -> str:
        return str(self.value)
