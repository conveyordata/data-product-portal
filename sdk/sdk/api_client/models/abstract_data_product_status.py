from enum import Enum


class AbstractDataProductStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETING = "deleting"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
