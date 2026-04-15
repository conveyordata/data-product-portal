from enum import Enum


class TechnicalMapping(str, Enum):
    CUSTOM = "custom"
    DEFAULT = "default"

    def __str__(self) -> str:
        return str(self.value)
