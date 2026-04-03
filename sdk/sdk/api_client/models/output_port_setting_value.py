from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.data_product_setting import DataProductSetting


T = TypeVar("T", bound="OutputPortSettingValue")


@_attrs_define
class OutputPortSettingValue:
    """
    Attributes:
        id (UUID):
        data_product_setting_id (UUID):
        value (str):
        data_product_setting (DataProductSetting):
        output_port_id (UUID):
    """

    id: UUID
    data_product_setting_id: UUID
    value: str
    data_product_setting: DataProductSetting
    output_port_id: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        data_product_setting_id = str(self.data_product_setting_id)

        value = self.value

        data_product_setting = self.data_product_setting.to_dict()

        output_port_id = str(self.output_port_id)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "data_product_setting_id": data_product_setting_id,
                "value": value,
                "data_product_setting": data_product_setting,
                "output_port_id": output_port_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_product_setting import DataProductSetting

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        data_product_setting_id = UUID(d.pop("data_product_setting_id"))

        value = d.pop("value")

        data_product_setting = DataProductSetting.from_dict(
            d.pop("data_product_setting")
        )

        output_port_id = UUID(d.pop("output_port_id"))

        output_port_setting_value = cls(
            id=id,
            data_product_setting_id=data_product_setting_id,
            value=value,
            data_product_setting=data_product_setting,
            output_port_id=output_port_id,
        )

        output_port_setting_value.additional_properties = d
        return output_port_setting_value

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
