from enum import UNIQUE, StrEnum, verify


@verify(UNIQUE)
class DecisionStatus(StrEnum):
    APPROVED = "approved"
    PENDING = "pending"
    DENIED = "denied"


@verify(UNIQUE)
class AssignmentFilter(StrEnum):
    ALL = "all"
    ONLY_ASSIGNED = "only_assigned"
