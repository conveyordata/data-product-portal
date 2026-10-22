from enum import Enum


class DomainStatus(str, Enum):
    ACTIVE = "active"
    DELETING = "deleting"
