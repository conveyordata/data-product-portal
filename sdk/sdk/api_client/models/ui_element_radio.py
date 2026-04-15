from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.select_option import SelectOption


T = TypeVar("T", bound="UIElementRadio")


@_attrs_define
class UIElementRadio:
    """
    Attributes:
        max_count (int | None | Unset):  Default: 1.
        initial_value (None | str | Unset):
        options (list[SelectOption] | None | Unset):
    """

    max_count: int | None | Unset = 1
    initial_value: None | str | Unset = UNSET
    options: list[SelectOption] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        max_count: int | None | Unset
        if isinstance(self.max_count, Unset):
            max_count = UNSET
        else:
            max_count = self.max_count

        initial_value: None | str | Unset
        if isinstance(self.initial_value, Unset):
            initial_value = UNSET
        else:
            initial_value = self.initial_value

        options: list[dict[str, Any]] | None | Unset
        if isinstance(self.options, Unset):
            options = UNSET
        elif isinstance(self.options, list):
            options = []
            for options_type_0_item_data in self.options:
                options_type_0_item = options_type_0_item_data.to_dict()
                options.append(options_type_0_item)

        else:
            options = self.options

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if max_count is not UNSET:
            field_dict["max_count"] = max_count
        if initial_value is not UNSET:
            field_dict["initial_value"] = initial_value
        if options is not UNSET:
            field_dict["options"] = options

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.select_option import SelectOption

        d = dict(src_dict)

        def _parse_max_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_count = _parse_max_count(d.pop("max_count", UNSET))

        def _parse_initial_value(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        initial_value = _parse_initial_value(d.pop("initial_value", UNSET))

        def _parse_options(data: object) -> list[SelectOption] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                options_type_0 = []
                _options_type_0 = data
                for options_type_0_item_data in _options_type_0:
                    options_type_0_item = SelectOption.from_dict(
                        options_type_0_item_data
                    )

                    options_type_0.append(options_type_0_item)

                return options_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[SelectOption] | None | Unset, data)

        options = _parse_options(d.pop("options", UNSET))

        ui_element_radio = cls(
            max_count=max_count,
            initial_value=initial_value,
            options=options,
        )

        ui_element_radio.additional_properties = d
        return ui_element_radio

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
