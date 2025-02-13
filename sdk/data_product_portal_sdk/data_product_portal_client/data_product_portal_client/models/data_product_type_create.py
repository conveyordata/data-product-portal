from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_product_icon_key import DataProductIconKey

T = TypeVar("T", bound="DataProductTypeCreate")


@_attrs_define
class DataProductTypeCreate:
    """
    Attributes:
        name (str):
        description (str):
        icon_key (DataProductIconKey):
    """

    name: str
    description: str
    icon_key: DataProductIconKey
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        icon_key = self.icon_key.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "icon_key": icon_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        icon_key = DataProductIconKey(d.pop("icon_key"))

        data_product_type_create = cls(
            name=name,
            description=description,
            icon_key=icon_key,
        )

        data_product_type_create.additional_properties = d
        return data_product_type_create

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
