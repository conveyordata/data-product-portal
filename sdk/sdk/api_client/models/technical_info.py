from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TechnicalInfo")


@_attrs_define
class TechnicalInfo:
    """
    Attributes:
        environment_id (UUID):
        environment (str):
        info (None | str):
    """

    environment_id: UUID
    environment: str
    info: None | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        environment_id = str(self.environment_id)

        environment = self.environment

        info: None | str
        info = self.info

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "environment_id": environment_id,
                "environment": environment,
                "info": info,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        environment_id = UUID(d.pop("environment_id"))

        environment = d.pop("environment")

        def _parse_info(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        info = _parse_info(d.pop("info"))

        technical_info = cls(
            environment_id=environment_id,
            environment=environment,
            info=info,
        )

        technical_info.additional_properties = d
        return technical_info

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
