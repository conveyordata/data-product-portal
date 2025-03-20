from enum import StrEnum, unique


@unique
class DecisionStatus(StrEnum):
    APPROVED = "approved"
    PENDING = "pending"
    DENIED = "denied"
