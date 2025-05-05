from enum import Enum


class DataProductUserRole(str, Enum):
    OWNER = "owner"
    MEMBER = "member"
