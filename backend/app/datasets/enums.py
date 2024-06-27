from enum import Enum


class DatasetAccessType(str, Enum):
    PUBLIC = "public"
    RESTRICTED = "restricted"
