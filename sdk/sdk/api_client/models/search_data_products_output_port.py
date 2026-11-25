from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.access_mode import AccessMode


T = TypeVar("T", bound="SearchDataProductsOutputPort")


@_attrs_define
class SearchDataProductsOutputPort:
    """
    Attributes:
        id (UUID):
        name (str):
        description (str):
        access_modes (list[AccessMode]):
    """

    id: UUID
    name: str
    description: str
    access_modes: list[AccessMode]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        description = self.description

        access_modes = []
        for access_modes_item_data in self.access_modes:
            access_modes_item = access_modes_item_data.to_dict()
            access_modes.append(access_modes_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "access_modes": access_modes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_mode import AccessMode  # noqa: PLC0415

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        description = d.pop("description")

        access_modes = []
        _access_modes = d.pop("access_modes")
        for access_modes_item_data in _access_modes:
            access_modes_item = AccessMode.from_dict(access_modes_item_data)

            access_modes.append(access_modes_item)

        search_data_products_output_port = cls(
            id=id,
            name=name,
            description=description,
            access_modes=access_modes,
        )

        search_data_products_output_port.additional_properties = d
        return search_data_products_output_port

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
