from enum import Enum


class OutputPortStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    ARCHIVED = "archived"
