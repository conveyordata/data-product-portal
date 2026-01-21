from enum import UNIQUE, Enum, verify


@verify(UNIQUE)
class DataQualityStatus(str, Enum):
    PASS = "pass"  # noqa: S105
    FAIL = "fail"
    WARN = "warn"
    ERROR = "error"
    UNKNOWN = "unknown"
