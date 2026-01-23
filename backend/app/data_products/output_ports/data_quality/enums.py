from enum import UNIQUE, Enum, verify


@verify(UNIQUE)
class DataQualityStatus(StrEnum):
    PASS = "pass"  # noqa: S105
    FAIL = "fail"
    WARN = "warn"
    ERROR = "error"
    UNKNOWN = "unknown"
