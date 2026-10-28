from enum import StrEnum


class RenewalStatus(StrEnum):
    DENIED = "denied"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
