from enum import UNIQUE, StrEnum, verify


@verify(UNIQUE)
class FreshnessStatus(StrEnum):
    FRESH = "fresh"
    STALE = "stale"
    UNKNOWN = "unknown"
