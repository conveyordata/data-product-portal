from enum import StrEnum


class AccessDurationType(StrEnum):
    PERMANENT = "permanent"
    TIME_BOUND = "time_bound"

    def __str__(self) -> str:
        return str(self.value)
