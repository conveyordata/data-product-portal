from enum import Enum


class DataProductUserRole(Enum):
    OWNER = "owner"
    MEMBER = "member"


class DataProductMembershipStatus(str, Enum):
    APPROVED = "approved"
    PENDING_APPROVAL = "pending_approval"
    DENIED = "denied"
