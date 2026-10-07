from enum import StrEnum


class InputPortRequestDecision(StrEnum):
    APPROVED = "approved"
    CANCELLED = "cancelled"
    DENIED = "denied"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
