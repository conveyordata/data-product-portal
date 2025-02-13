from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_product_setting_scope import DataProductSettingScope
from ..models.data_product_setting_type import DataProductSettingType
from ..types import UNSET, Unset

T = TypeVar("T", bound="DataProductSettingUpdate")


@_attrs_define
class DataProductSettingUpdate:
    """
    Attributes:
        category (str):
        type_ (DataProductSettingType):
        tooltip (str):
        external_id (str):
        name (str):
        default (str):
        scope (DataProductSettingScope):
        order (Union[Unset, int]):  Default: 100.
    """

    category: str
    type_: DataProductSettingType
    tooltip: str
    external_id: str
    name: str
    default: str
    scope: DataProductSettingScope
    order: Union[Unset, int] = 100
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        category = self.category

        type_ = self.type_.value

        tooltip = self.tooltip

        external_id = self.external_id

        name = self.name

        default = self.default

        scope = self.scope.value

        order = self.order

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "category": category,
                "type": type_,
                "tooltip": tooltip,
                "external_id": external_id,
                "name": name,
                "default": default,
                "scope": scope,
            }
        )
        if order is not UNSET:
            field_dict["order"] = order

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        category = d.pop("category")

        type_ = DataProductSettingType(d.pop("type"))

        tooltip = d.pop("tooltip")

        external_id = d.pop("external_id")

        name = d.pop("name")

        default = d.pop("default")

        scope = DataProductSettingScope(d.pop("scope"))

        order = d.pop("order", UNSET)

        data_product_setting_update = cls(
            category=category,
            type_=type_,
            tooltip=tooltip,
            external_id=external_id,
            name=name,
            default=default,
            scope=scope,
            order=order,
        )

        data_product_setting_update.additional_properties = d
        return data_product_setting_update

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
