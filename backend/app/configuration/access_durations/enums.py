from enum import UNIQUE, Enum, verify


@verify(UNIQUE)
class AccessDurationType(str, Enum):
    PERMANENT = "permanent"
    TIME_BOUND = "time_bound"
