from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.platform_tile import PlatformTile


T = TypeVar("T", bound="PlatformTileResponse")


@_attrs_define
class PlatformTileResponse:
    """Response model for platform tiles

    Attributes:
        platform_tiles (list[PlatformTile]):
    """

    platform_tiles: list[PlatformTile]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        platform_tiles = []
        for platform_tiles_item_data in self.platform_tiles:
            platform_tiles_item = platform_tiles_item_data.to_dict()
            platform_tiles.append(platform_tiles_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "platform_tiles": platform_tiles,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.platform_tile import PlatformTile

        d = dict(src_dict)
        platform_tiles = []
        _platform_tiles = d.pop("platform_tiles")
        for platform_tiles_item_data in _platform_tiles:
            platform_tiles_item = PlatformTile.from_dict(platform_tiles_item_data)

            platform_tiles.append(platform_tiles_item)

        platform_tile_response = cls(
            platform_tiles=platform_tiles,
        )

        platform_tile_response.additional_properties = d
        return platform_tile_response

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
