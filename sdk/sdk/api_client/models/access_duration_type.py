from enum import Enum


class AccessDurationType(str, Enum):
    PERMANENT = "permanent"
    TIME_BOUND = "time_bound"

    def __str__(self) -> str:
        return str(self.value)
