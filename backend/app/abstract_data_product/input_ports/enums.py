from enum import UNIQUE, StrEnum, verify


@verify(UNIQUE)
class RenewalStatus(StrEnum):
    PENDING = "pending"
    DENIED = "denied"


@verify(UNIQUE)
class InputPortStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    REVOKED = "revoked"
    CANCELLED = "cancelled"


@verify(UNIQUE)
class InputPortRequestDecision(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELLED = "cancelled"
