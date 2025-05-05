from enum import Enum
from typing import Optional
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
    authz_code: Optional[str]
    authz_state: Optional[str]
    authz_verif: Optional[str]

    @computed_field
    def verification_uri_complete(self) -> str:
        return (
            f"{self.oidc_redirect_uri}api/auth/"
            f"device?code={self.user_code}&authorize=true"
        )
