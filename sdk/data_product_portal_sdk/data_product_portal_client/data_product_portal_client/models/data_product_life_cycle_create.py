from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DataProductLifeCycleCreate")


@_attrs_define
class DataProductLifeCycleCreate:
    """
    Attributes:
        value (int):
        name (str):
        color (str):
        is_default (Union[Unset, bool]):  Default: False.
    """

    value: int
    name: str
    color: str
    is_default: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = self.value

        name = self.name

        color = self.color

        is_default = self.is_default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "value": value,
                "name": name,
                "color": color,
            }
        )
        if is_default is not UNSET:
            field_dict["is_default"] = is_default

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        value = d.pop("value")

        name = d.pop("name")

        color = d.pop("color")

        is_default = d.pop("is_default", UNSET)

        data_product_life_cycle_create = cls(
            value=value,
            name=name,
            color=color,
            is_default=is_default,
        )

        data_product_life_cycle_create.additional_properties = d
        return data_product_life_cycle_create

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
