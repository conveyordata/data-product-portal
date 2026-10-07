from enum import StrEnum


class AssignmentFilter(StrEnum):
    ALL = "all"
    ONLY_ASSIGNED = "only_assigned"

    def __str__(self) -> str:
        return str(self.value)
