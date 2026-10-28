from enum import StrEnum


class OutputPortAccessFunction(StrEnum):
    PRIVATE = "private"
    RESTRICTED = "restricted"
    UNRESTRICTED = "unrestricted"

    def __str__(self) -> str:
        return str(self.value)
