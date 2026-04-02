from enum import Enum


class ResourceNameValidityType(str, Enum):
    DUPLICATE = "DUPLICATE"
    INVALID_CHARACTERS = "INVALID_CHARACTERS"
    INVALID_LENGTH = "INVALID_LENGTH"
    VALID = "VALID"

    def __str__(self) -> str:
        return str(self.value)
