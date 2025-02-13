from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.device_flow_status import DeviceFlowStatus

T = TypeVar("T", bound="DeviceFlow")


@_attrs_define
class DeviceFlow:
    """
    Attributes:
        device_code (UUID):
        user_code (str):
        scope (str):
        interval (int):
        expiration (int):
        oidc_redirect_uri (str):
        status (DeviceFlowStatus):
        authz_code (Union[None, str]):
        authz_state (Union[None, str]):
        authz_verif (Union[None, str]):
        verification_uri_complete (str):
    """

    device_code: UUID
    user_code: str
    scope: str
    interval: int
    expiration: int
    oidc_redirect_uri: str
    status: DeviceFlowStatus
    authz_code: Union[None, str]
    authz_state: Union[None, str]
    authz_verif: Union[None, str]
    verification_uri_complete: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_code = str(self.device_code)

        user_code = self.user_code

        scope = self.scope

        interval = self.interval

        expiration = self.expiration

        oidc_redirect_uri = self.oidc_redirect_uri

        status = self.status.value

        authz_code: Union[None, str]
        authz_code = self.authz_code

        authz_state: Union[None, str]
        authz_state = self.authz_state

        authz_verif: Union[None, str]
        authz_verif = self.authz_verif

        verification_uri_complete = self.verification_uri_complete

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_code": device_code,
                "user_code": user_code,
                "scope": scope,
                "interval": interval,
                "expiration": expiration,
                "oidc_redirect_uri": oidc_redirect_uri,
                "status": status,
                "authz_code": authz_code,
                "authz_state": authz_state,
                "authz_verif": authz_verif,
                "verification_uri_complete": verification_uri_complete,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        device_code = UUID(d.pop("device_code"))

        user_code = d.pop("user_code")

        scope = d.pop("scope")

        interval = d.pop("interval")

        expiration = d.pop("expiration")

        oidc_redirect_uri = d.pop("oidc_redirect_uri")

        status = DeviceFlowStatus(d.pop("status"))

        def _parse_authz_code(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        authz_code = _parse_authz_code(d.pop("authz_code"))

        def _parse_authz_state(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        authz_state = _parse_authz_state(d.pop("authz_state"))

        def _parse_authz_verif(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        authz_verif = _parse_authz_verif(d.pop("authz_verif"))

        verification_uri_complete = d.pop("verification_uri_complete")

        device_flow = cls(
            device_code=device_code,
            user_code=user_code,
            scope=scope,
            interval=interval,
            expiration=expiration,
            oidc_redirect_uri=oidc_redirect_uri,
            status=status,
            authz_code=authz_code,
            authz_state=authz_state,
            authz_verif=authz_verif,
            verification_uri_complete=verification_uri_complete,
        )

        device_flow.additional_properties = d
        return device_flow

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
