from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OIDCTokenResponse")


@_attrs_define
class OIDCTokenResponse:
    """OIDC token endpoint response.

    Attributes:
        access_token (str):
        token_type (str):
        expires_in (int):
        id_token (None | str | Unset):
        refresh_token (None | str | Unset):
    """

    access_token: str
    token_type: str
    expires_in: int
    id_token: None | str | Unset = UNSET
    refresh_token: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_token = self.access_token

        token_type = self.token_type

        expires_in = self.expires_in

        id_token: None | str | Unset
        if isinstance(self.id_token, Unset):
            id_token = UNSET
        else:
            id_token = self.id_token

        refresh_token: None | str | Unset
        if isinstance(self.refresh_token, Unset):
            refresh_token = UNSET
        else:
            refresh_token = self.refresh_token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "access_token": access_token,
                "token_type": token_type,
                "expires_in": expires_in,
            }
        )
        if id_token is not UNSET:
            field_dict["id_token"] = id_token
        if refresh_token is not UNSET:
            field_dict["refresh_token"] = refresh_token

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        access_token = d.pop("access_token")

        token_type = d.pop("token_type")

        expires_in = d.pop("expires_in")

        def _parse_id_token(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        id_token = _parse_id_token(d.pop("id_token", UNSET))

        def _parse_refresh_token(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        refresh_token = _parse_refresh_token(d.pop("refresh_token", UNSET))

        oidc_token_response = cls(
            access_token=access_token,
            token_type=token_type,
            expires_in=expires_in,
            id_token=id_token,
            refresh_token=refresh_token,
        )

        oidc_token_response.additional_properties = d
        return oidc_token_response

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
