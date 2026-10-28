from enum import StrEnum


class DataProductVisibility(StrEnum):
    DISCOVERABLE = "discoverable"
    HIDDEN = "hidden"

    def __str__(self) -> str:
        return str(self.value)
