from enum import UNIQUE, Enum, verify


@verify(UNIQUE)
class DataQualityStatus(str, Enum):
    PASS = "pass"  # noqa: S105
    FAIL = "fail"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"
