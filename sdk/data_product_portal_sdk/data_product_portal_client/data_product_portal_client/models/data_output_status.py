from enum import Enum


class DataOutputStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
