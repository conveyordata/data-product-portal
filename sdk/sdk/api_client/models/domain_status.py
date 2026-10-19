from enum import StrEnum


class DomainStatus(StrEnum):
    ACTIVE = "active"
    DELETING = "deleting"

    def __str__(self) -> str:
        return str(self.value)
