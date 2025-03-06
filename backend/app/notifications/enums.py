from enum import Enum


class NotificationTrigger(str, Enum):
    ACTION_APPROVED = "action_approved"
    ACTION_DENIED = "action_denied"
    ACTION_REQUESTED = "action_requested"
