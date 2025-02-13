from enum import Enum


class DataProductSettingType(str, Enum):
    CHECKBOX = "checkbox"
    INPUT = "input"
    TAGS = "tags"

    def __str__(self) -> str:
        return str(self.value)
