from enum import Enum


class UIElementType(str, Enum):
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SELECT = "select"
    STRING = "string"

    def __str__(self) -> str:
        return str(self.value)
