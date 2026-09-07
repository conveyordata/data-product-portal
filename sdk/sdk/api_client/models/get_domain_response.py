from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.environment_get_item import EnvironmentGetItem


T = TypeVar("T", bound="GetDomainResponse")


@_attrs_define
class GetDomainResponse:
    """
    Attributes:
        id (UUID):
        name (str):
        description (str):
        environments (list[EnvironmentGetItem]):
    """

    id: UUID
    name: str
    description: str
    environments: list[EnvironmentGetItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        description = self.description

        environments = []
        for environments_item_data in self.environments:
            environments_item = environments_item_data.to_dict()
            environments.append(environments_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "environments": environments,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.environment_get_item import EnvironmentGetItem

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        description = d.pop("description")

        environments = []
        _environments = d.pop("environments")
        for environments_item_data in _environments:
            environments_item = EnvironmentGetItem.from_dict(environments_item_data)

            environments.append(environments_item)

        get_domain_response = cls(
            id=id,
            name=name,
            description=description,
            environments=environments,
        )

        get_domain_response.additional_properties = d
        return get_domain_response

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
