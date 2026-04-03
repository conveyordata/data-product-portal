from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_product_setting_scope import DataProductSettingScope
from ..models.data_product_setting_type import DataProductSettingType
from ..types import UNSET, Unset

T = TypeVar("T", bound="DataProductSettingsGetItem")


@_attrs_define
class DataProductSettingsGetItem:
    """
    Attributes:
        id (UUID):
        category (str):
        type_ (DataProductSettingType):
        tooltip (str):
        namespace (str):
        name (str):
        default (str):
        scope (DataProductSettingScope):
        order (int | Unset):  Default: 100.
    """

    id: UUID
    category: str
    type_: DataProductSettingType
    tooltip: str
    namespace: str
    name: str
    default: str
    scope: DataProductSettingScope
    order: int | Unset = 100
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        category = self.category

        type_ = self.type_.value

        tooltip = self.tooltip

        namespace = self.namespace

        name = self.name

        default = self.default

        scope = self.scope.value

        order = self.order

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "category": category,
                "type": type_,
                "tooltip": tooltip,
                "namespace": namespace,
                "name": name,
                "default": default,
                "scope": scope,
            }
        )
        if order is not UNSET:
            field_dict["order"] = order

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        category = d.pop("category")

        type_ = DataProductSettingType(d.pop("type"))

        tooltip = d.pop("tooltip")

        namespace = d.pop("namespace")

        name = d.pop("name")

        default = d.pop("default")

        scope = DataProductSettingScope(d.pop("scope"))

        order = d.pop("order", UNSET)

        data_product_settings_get_item = cls(
            id=id,
            category=category,
            type_=type_,
            tooltip=tooltip,
            namespace=namespace,
            name=name,
            default=default,
            scope=scope,
            order=order,
        )

        data_product_settings_get_item.additional_properties = d
        return data_product_settings_get_item

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
