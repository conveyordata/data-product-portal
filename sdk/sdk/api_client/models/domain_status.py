from enum import Enum


class DomainStatus(str, Enum):
    ACTIVE = "active"
    DELETING = "deleting"

    def __str__(self) -> str:
        return str(self.value)
