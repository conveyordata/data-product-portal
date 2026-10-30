from enum import Enum


class AnnouncementType(str, Enum):
    ACTION_NEEDED = "action_needed"
    WARNING = "warning"
    INFO = "info"
