from enum import Enum


class DataQualityStatus(str, Enum):
    ERROR = "error"
    FAILURE = "failure"
    SUCCESS = "success"
    UNKNOWN = "unknown"
    WARNING = "warning"

    def __str__(self) -> str:
        return str(self.value)
