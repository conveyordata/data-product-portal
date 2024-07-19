from enum import Enum


class DatasetAccessType(str, Enum):
    PUBLIC = "public"
    RESTRICTED = "restricted"

class DatasetType(str, Enum):
    TABLE = "table"
    SYSTEM = "system"
    DOCUMENT = "document"
    FILE = "file"