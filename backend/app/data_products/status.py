from enum import Enum


class AbstractDataProductStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETING = "deleting"
