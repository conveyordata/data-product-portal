from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PostgreSQLConfig")


@_attrs_define
class PostgreSQLConfig:
    """
    Attributes:
        identifier (str):
        host (str):
        port (str):
        admin_user (str):
        admin_pwd (str):
    """

    identifier: str
    host: str
    port: str
    admin_user: str
    admin_pwd: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        identifier = self.identifier

        host = self.host

        port = self.port

        admin_user = self.admin_user

        admin_pwd = self.admin_pwd

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identifier": identifier,
                "host": host,
                "port": port,
                "admin_user": admin_user,
                "admin_pwd": admin_pwd,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        identifier = d.pop("identifier")

        host = d.pop("host")

        port = d.pop("port")

        admin_user = d.pop("admin_user")

        admin_pwd = d.pop("admin_pwd")

        postgre_sql_config = cls(
            identifier=identifier,
            host=host,
            port=port,
            admin_user=admin_user,
            admin_pwd=admin_pwd,
        )

        postgre_sql_config.additional_properties = d
        return postgre_sql_config

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
