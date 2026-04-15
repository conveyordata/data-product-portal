from enum import Enum


class AccessGranularity(str, Enum):
    SCHEMA = "schema"
    TABLE = "table"

    def __str__(self) -> str:
        return str(self.value)
