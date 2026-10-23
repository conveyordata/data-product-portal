from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="EnvironmentConfigurationValue")


@_attrs_define
class EnvironmentConfigurationValue:
    """
    Attributes:
        environment_id (UUID):
        name (str):
        acronym (str):
        override (None | str):
        effective_value (str):
    """

    environment_id: UUID
    name: str
    acronym: str
    override: None | str
    effective_value: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        environment_id = str(self.environment_id)

        name = self.name

        acronym = self.acronym

        override: None | str
        override = self.override

        effective_value = self.effective_value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "environment_id": environment_id,
                "name": name,
                "acronym": acronym,
                "override": override,
                "effective_value": effective_value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        environment_id = UUID(d.pop("environment_id"))

        name = d.pop("name")

        acronym = d.pop("acronym")

        def _parse_override(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        override = _parse_override(d.pop("override"))

        effective_value = d.pop("effective_value")

        environment_configuration_value = cls(
            environment_id=environment_id,
            name=name,
            acronym=acronym,
            override=override,
            effective_value=effective_value,
        )

        environment_configuration_value.additional_properties = d
        return environment_configuration_value

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
