from enum import StrEnum


class DeviceFlowStatus(StrEnum):
    AUTHORIZATION_PENDING = "authorization_pending"
    AUTHORIZED = "authorized"
    DENIED = "denied"
    EXPIRED = "expired"

    def __str__(self) -> str:
        return str(self.value)
