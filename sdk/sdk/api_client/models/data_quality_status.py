from enum import StrEnum


class DataQualityStatus(StrEnum):
    ERROR = "error"
    FAILURE = "failure"
    SUCCESS = "success"
    UNKNOWN = "unknown"
    WARNING = "warning"

    def __str__(self) -> str:
        return str(self.value)
