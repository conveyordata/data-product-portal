from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UIElementCheckbox")


@_attrs_define
class UIElementCheckbox:
    """
    Attributes:
        initial_value (bool | None | Unset):
    """

    initial_value: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        initial_value: bool | None | Unset
        if isinstance(self.initial_value, Unset):
            initial_value = UNSET
        else:
            initial_value = self.initial_value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if initial_value is not UNSET:
            field_dict["initial_value"] = initial_value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_initial_value(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        initial_value = _parse_initial_value(d.pop("initial_value", UNSET))

        ui_element_checkbox = cls(
            initial_value=initial_value,
        )

        ui_element_checkbox.additional_properties = d
        return ui_element_checkbox

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
