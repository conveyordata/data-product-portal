from enum import Enum


class RenewalStatus(str, Enum):
    DENIED = "denied"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
