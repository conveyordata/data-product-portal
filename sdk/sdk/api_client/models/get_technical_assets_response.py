from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_technical_assets_response_item import (
        GetTechnicalAssetsResponseItem,
    )


T = TypeVar("T", bound="GetTechnicalAssetsResponse")


@_attrs_define
class GetTechnicalAssetsResponse:
    """
    Attributes:
        technical_assets (list[GetTechnicalAssetsResponseItem]):
    """

    technical_assets: list[GetTechnicalAssetsResponseItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        technical_assets = []
        for technical_assets_item_data in self.technical_assets:
            technical_assets_item = technical_assets_item_data.to_dict()
            technical_assets.append(technical_assets_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "technical_assets": technical_assets,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_technical_assets_response_item import (
            GetTechnicalAssetsResponseItem,
        )

        d = dict(src_dict)
        technical_assets = []
        _technical_assets = d.pop("technical_assets")
        for technical_assets_item_data in _technical_assets:
            technical_assets_item = GetTechnicalAssetsResponseItem.from_dict(
                technical_assets_item_data
            )

            technical_assets.append(technical_assets_item)

        get_technical_assets_response = cls(
            technical_assets=technical_assets,
        )

        get_technical_assets_response.additional_properties = d
        return get_technical_assets_response

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
