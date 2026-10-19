from enum import StrEnum


class AbstractDataProductStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETING = "deleting"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
