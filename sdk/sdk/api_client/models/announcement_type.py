from enum import StrEnum


class AnnouncementType(StrEnum):
    ACTION_NEEDED = "action_needed"
    INFO = "info"
    WARNING = "warning"

    def __str__(self) -> str:
        return str(self.value)
