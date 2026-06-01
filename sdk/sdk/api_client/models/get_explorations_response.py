from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.exploration import Exploration


T = TypeVar("T", bound="GetExplorationsResponse")


@_attrs_define
class GetExplorationsResponse:
    """
    Attributes:
        explorations (list[Exploration]):
    """

    explorations: list[Exploration]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        explorations = []
        for explorations_item_data in self.explorations:
            explorations_item = explorations_item_data.to_dict()
            explorations.append(explorations_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "explorations": explorations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.exploration import Exploration

        d = dict(src_dict)
        explorations = []
        _explorations = d.pop("explorations")
        for explorations_item_data in _explorations:
            explorations_item = Exploration.from_dict(explorations_item_data)

            explorations.append(explorations_item)

        get_explorations_response = cls(
            explorations=explorations,
        )

        get_explorations_response.additional_properties = d
        return get_explorations_response

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
