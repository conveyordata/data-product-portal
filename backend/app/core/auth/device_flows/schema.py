from enum import Enum
from uuid import UUID

from pydantic import computed_field

from app.shared.schema import ORMModel


class DeviceFlowStatus(str, Enum):
    AUTHORIZATION_PENDING = "authorization_pending"
    EXPIRED = "expired"
    DENIED = "denied"
    AUTHORIZED = "authorized"


class DeviceFlow(ORMModel):
    device_code: UUID
    user_code: str
    scope: str
    interval: int
    expiration: int
    oidc_redirect_uri: str
    status: DeviceFlowStatus
    authz_code: str | None
    authz_state: str | None
    authz_verif: str | None

    @computed_field
    def verification_uri_complete(self) -> str:
        return (
            f"{self.oidc_redirect_uri}api/auth/"
            f"device?code={self.user_code}&authorize=true"
        )
