from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DomainUpdate")


@_attrs_define
class DomainUpdate:
    """
    Attributes:
        name (str):
        description (str):
        environment_ids (list[UUID] | Unset):
    """

    name: str
    description: str
    environment_ids: list[UUID] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        environment_ids: list[str] | Unset = UNSET
        if not isinstance(self.environment_ids, Unset):
            environment_ids = []
            for environment_ids_item_data in self.environment_ids:
                environment_ids_item = str(environment_ids_item_data)
                environment_ids.append(environment_ids_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
            }
        )
        if environment_ids is not UNSET:
            field_dict["environment_ids"] = environment_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        _environment_ids = d.pop("environment_ids", UNSET)
        environment_ids: list[UUID] | Unset = UNSET
        if _environment_ids is not UNSET:
            environment_ids = []
            for environment_ids_item_data in _environment_ids:
                environment_ids_item = UUID(environment_ids_item_data)

                environment_ids.append(environment_ids_item)

        domain_update = cls(
            name=name,
            description=description,
            environment_ids=environment_ids,
        )

        domain_update.additional_properties = d
        return domain_update

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
