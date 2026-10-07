from enum import StrEnum


class UIElementType(StrEnum):
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SELECT = "select"
    STRING = "string"

    def __str__(self) -> str:
        return str(self.value)
