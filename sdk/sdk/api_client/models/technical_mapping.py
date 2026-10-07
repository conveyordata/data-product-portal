from enum import StrEnum


class TechnicalMapping(StrEnum):
    CUSTOM = "custom"
    DEFAULT = "default"

    def __str__(self) -> str:
        return str(self.value)
