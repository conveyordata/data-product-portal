from enum import Enum


class DataProductVisibility(str, Enum):
    DISCOVERABLE = "discoverable"
    HIDDEN = "hidden"

    def __str__(self) -> str:
        return str(self.value)
