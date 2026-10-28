from enum import StrEnum


class AnnouncementType(StrEnum):
    ACTION_NEEDED = "action_needed"
    INFO = "info"
    ISSUE = "issue"
    NEW_VERSION = "new_version"
    PLANNED_MAINTENANCE = "planned_maintenance"

    def __str__(self) -> str:
        return str(self.value)
