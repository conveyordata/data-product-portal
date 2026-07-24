from enum import Enum


class InputPortStatus(str, Enum):
    APPROVED = "approved"
    CANCELLED = "cancelled"
    DENIED = "denied"
    EXPIRED = "expired"
    PENDING = "pending"
    REVOKED = "revoked"

    def __str__(self) -> str:
        return str(self.value)
