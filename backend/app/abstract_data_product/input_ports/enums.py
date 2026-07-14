from enum import UNIQUE, StrEnum, verify


@verify(UNIQUE)
class InputPortStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
