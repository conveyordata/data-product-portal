from enum import Enum


class OutputPortAccessType(str, Enum):
    PUBLIC = "public"
    RESTRICTED = "restricted"
    PRIVATE = "private"
