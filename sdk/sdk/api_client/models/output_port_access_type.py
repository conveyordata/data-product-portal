from enum import Enum


class OutputPortAccessType(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    RESTRICTED = "restricted"
    UNRESTRICTED = "unrestricted"

    def __str__(self) -> str:
        return str(self.value)
