import uuid
from string import ascii_lowercase, digits

from shortuuid import ShortUUID
from sqlalchemy import UUID, Column, Enum, Integer, String

from app.core.auth.device_flows.schema import DeviceFlowStatus
from app.database.database import Base
from app.shared.model import BaseORM, UTCDateTime, utcnow

alphabet = ascii_lowercase + digits
su = ShortUUID(alphabet=alphabet)


def generate_user_code():
    return su.random(length=8).upper()


class DeviceFlow(Base, BaseORM):
    __tablename__ = "device_flows"
    device_code = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_code = Column(String, default=generate_user_code)
    scope = Column(String, default="openid")
    interval = Column(Integer, default=5)
    expiration = Column(Integer, default=1800)
    status: DeviceFlowStatus = Column(
        Enum(DeviceFlowStatus), default=DeviceFlowStatus.AUTHORIZATION_PENDING
    )
    client_id = Column(String)
    max_expiry = Column(UTCDateTime())
    last_checked = Column(UTCDateTime(), server_default=utcnow())
    oidc_redirect_uri = Column(String)
    authz_code = Column(String)
    authz_state = Column(String)
    authz_verif = Column(String)
