from enum import Enum


class OutputPortAccessType(str, Enum):
    PUBLIC = "public"  # Deprecated: use unrestricted instead
    RESTRICTED = "restricted"
    PRIVATE = "private"
    UNRESTRICTED = "unrestricted"
