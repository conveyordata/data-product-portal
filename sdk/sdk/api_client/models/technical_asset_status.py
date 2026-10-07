from enum import StrEnum


class TechnicalAssetStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
