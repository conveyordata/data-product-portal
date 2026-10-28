from enum import StrEnum


class InputPortStatus(StrEnum):
    APPROVED = "approved"
    CANCELLED = "cancelled"
    DENIED = "denied"
    EXPIRED = "expired"
    PENDING = "pending"
    REVOKED = "revoked"

    def __str__(self) -> str:
        return str(self.value)
