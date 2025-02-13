from enum import Enum


class DataProductStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
