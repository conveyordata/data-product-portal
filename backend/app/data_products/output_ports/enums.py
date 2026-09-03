from enum import Enum


class OutputPortAccessType(str, Enum):
    RESTRICTED = "restricted"
    PRIVATE = "private"
    UNRESTRICTED = "unrestricted"

    @classmethod
    def _missing_(cls, value):
        if value == "public":
            return cls.UNRESTRICTED
        return None
