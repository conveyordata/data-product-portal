from enum import Enum


class InputPortRequestDecision(str, Enum):
    APPROVED = "approved"
    CANCELLED = "cancelled"
    DENIED = "denied"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
