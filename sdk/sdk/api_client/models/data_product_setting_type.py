from enum import StrEnum


class DataProductSettingType(StrEnum):
    CHECKBOX = "checkbox"
    INPUT = "input"
    TAGS = "tags"

    def __str__(self) -> str:
        return str(self.value)
