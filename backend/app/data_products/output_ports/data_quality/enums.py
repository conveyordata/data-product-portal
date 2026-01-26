from enum import UNIQUE, StrEnum, verify


@verify(UNIQUE)
class DataQualityStatus(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"
