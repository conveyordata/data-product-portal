from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.data_product_setting_value import DataProductSettingValue


T = TypeVar("T", bound="GetDataProductSettingsResponse")


@_attrs_define
class GetDataProductSettingsResponse:
    """
    Attributes:
        data_product_settings (list[DataProductSettingValue]):
    """

    data_product_settings: list[DataProductSettingValue]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_product_settings = []
        for data_product_settings_item_data in self.data_product_settings:
            data_product_settings_item = data_product_settings_item_data.to_dict()
            data_product_settings.append(data_product_settings_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_product_settings": data_product_settings,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_product_setting_value import DataProductSettingValue

        d = dict(src_dict)
        data_product_settings = []
        _data_product_settings = d.pop("data_product_settings")
        for data_product_settings_item_data in _data_product_settings:
            data_product_settings_item = DataProductSettingValue.from_dict(
                data_product_settings_item_data
            )

            data_product_settings.append(data_product_settings_item)

        get_data_product_settings_response = cls(
            data_product_settings=data_product_settings,
        )

        get_data_product_settings_response.additional_properties = d
        return get_data_product_settings_response

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
