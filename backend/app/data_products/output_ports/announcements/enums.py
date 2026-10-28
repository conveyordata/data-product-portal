from enum import Enum


class AnnouncementType(str, Enum):
    ISSUE = "issue"
    ACTION_NEEDED = "action_needed"
    PLANNED_MAINTENANCE = "planned_maintenance"
    NEW_VERSION = "new_version"
    INFO = "info"
