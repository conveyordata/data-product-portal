from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_data_product_response import GetDataProductResponse
    from ..models.get_technical_assets_response_item import (
        GetTechnicalAssetsResponseItem,
    )


T = TypeVar("T", bound="TechnicalAssetLinkDeniedEvent")


@_attrs_define
class TechnicalAssetLinkDeniedEvent:
    """
    Attributes:
        data_product (GetDataProductResponse):
        technical_asset (GetTechnicalAssetsResponseItem):
    """

    data_product: GetDataProductResponse
    technical_asset: GetTechnicalAssetsResponseItem
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_product = self.data_product.to_dict()

        technical_asset = self.technical_asset.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_product": data_product,
                "technical_asset": technical_asset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_data_product_response import GetDataProductResponse
        from ..models.get_technical_assets_response_item import (
            GetTechnicalAssetsResponseItem,
        )

        d = dict(src_dict)
        data_product = GetDataProductResponse.from_dict(d.pop("data_product"))

        technical_asset = GetTechnicalAssetsResponseItem.from_dict(
            d.pop("technical_asset")
        )

        technical_asset_link_denied_event = cls(
            data_product=data_product,
            technical_asset=technical_asset,
        )

        technical_asset_link_denied_event.additional_properties = d
        return technical_asset_link_denied_event

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
