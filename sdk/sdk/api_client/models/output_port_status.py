from enum import StrEnum


class OutputPortStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
