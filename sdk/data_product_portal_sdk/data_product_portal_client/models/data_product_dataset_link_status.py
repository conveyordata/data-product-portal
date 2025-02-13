from enum import Enum


class DataProductDatasetLinkStatus(str, Enum):
    APPROVED = "approved"
    DENIED = "denied"
    PENDING_APPROVAL = "pending_approval"

    def __str__(self) -> str:
        return str(self.value)
