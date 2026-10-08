from enum import Enum


class OutputPortAccessFunction(str, Enum):
    PRIVATE = "private"
    RESTRICTED = "restricted"
    UNRESTRICTED = "unrestricted"

    def __str__(self) -> str:
        return str(self.value)
