from enum import UNIQUE, StrEnum, verify


@verify(UNIQUE)
class DecisionStatus(StrEnum):
    APPROVED = "approved"
    PENDING = "pending"
    DENIED = "denied"
