from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.platform_tile import PlatformTile
    from ..models.ui_element_metadata import UIElementMetadata


T = TypeVar("T", bound="UIElementMetadataResponse")


@_attrs_define
class UIElementMetadataResponse:
    """
    Attributes:
        ui_metadata (list[UIElementMetadata]):
        plugin (str):
        has_environments (bool):
        platform (str):
        display_name (str):
        icon_name (str):
        detailed_name (str):
        not_configured (bool | Unset):  Default: False.
        result_label (str | Unset):  Default: 'Resulting path'.
        result_tooltip (str | Unset):  Default: 'The path you can access through this technical asset'.
        parent_platform (None | str | Unset):
        platform_tile (None | PlatformTile | Unset):
        show_in_form (bool | Unset):  Default: True.
    """

    ui_metadata: list[UIElementMetadata]
    plugin: str
    has_environments: bool
    platform: str
    display_name: str
    icon_name: str
    detailed_name: str
    not_configured: bool | Unset = False
    result_label: str | Unset = "Resulting path"
    result_tooltip: str | Unset = "The path you can access through this technical asset"
    parent_platform: None | str | Unset = UNSET
    platform_tile: None | PlatformTile | Unset = UNSET
    show_in_form: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.platform_tile import PlatformTile

        ui_metadata = []
        for ui_metadata_item_data in self.ui_metadata:
            ui_metadata_item = ui_metadata_item_data.to_dict()
            ui_metadata.append(ui_metadata_item)

        plugin = self.plugin

        has_environments = self.has_environments

        platform = self.platform

        display_name = self.display_name

        icon_name = self.icon_name

        detailed_name = self.detailed_name

        not_configured = self.not_configured

        result_label = self.result_label

        result_tooltip = self.result_tooltip

        parent_platform: None | str | Unset
        if isinstance(self.parent_platform, Unset):
            parent_platform = UNSET
        else:
            parent_platform = self.parent_platform

        platform_tile: dict[str, Any] | None | Unset
        if isinstance(self.platform_tile, Unset):
            platform_tile = UNSET
        elif isinstance(self.platform_tile, PlatformTile):
            platform_tile = self.platform_tile.to_dict()
        else:
            platform_tile = self.platform_tile

        show_in_form = self.show_in_form

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ui_metadata": ui_metadata,
                "plugin": plugin,
                "has_environments": has_environments,
                "platform": platform,
                "display_name": display_name,
                "icon_name": icon_name,
                "detailed_name": detailed_name,
            }
        )
        if not_configured is not UNSET:
            field_dict["not_configured"] = not_configured
        if result_label is not UNSET:
            field_dict["result_label"] = result_label
        if result_tooltip is not UNSET:
            field_dict["result_tooltip"] = result_tooltip
        if parent_platform is not UNSET:
            field_dict["parent_platform"] = parent_platform
        if platform_tile is not UNSET:
            field_dict["platform_tile"] = platform_tile
        if show_in_form is not UNSET:
            field_dict["show_in_form"] = show_in_form

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.platform_tile import PlatformTile
        from ..models.ui_element_metadata import UIElementMetadata

        d = dict(src_dict)
        ui_metadata = []
        _ui_metadata = d.pop("ui_metadata")
        for ui_metadata_item_data in _ui_metadata:
            ui_metadata_item = UIElementMetadata.from_dict(ui_metadata_item_data)

            ui_metadata.append(ui_metadata_item)

        plugin = d.pop("plugin")

        has_environments = d.pop("has_environments")

        platform = d.pop("platform")

        display_name = d.pop("display_name")

        icon_name = d.pop("icon_name")

        detailed_name = d.pop("detailed_name")

        not_configured = d.pop("not_configured", UNSET)

        result_label = d.pop("result_label", UNSET)

        result_tooltip = d.pop("result_tooltip", UNSET)

        def _parse_parent_platform(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        parent_platform = _parse_parent_platform(d.pop("parent_platform", UNSET))

        def _parse_platform_tile(data: object) -> None | PlatformTile | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                platform_tile_type_0 = PlatformTile.from_dict(data)

                return platform_tile_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PlatformTile | Unset, data)

        platform_tile = _parse_platform_tile(d.pop("platform_tile", UNSET))

        show_in_form = d.pop("show_in_form", UNSET)

        ui_element_metadata_response = cls(
            ui_metadata=ui_metadata,
            plugin=plugin,
            has_environments=has_environments,
            platform=platform,
            display_name=display_name,
            icon_name=icon_name,
            detailed_name=detailed_name,
            not_configured=not_configured,
            result_label=result_label,
            result_tooltip=result_tooltip,
            parent_platform=parent_platform,
            platform_tile=platform_tile,
            show_in_form=show_in_form,
        )

        ui_element_metadata_response.additional_properties = d
        return ui_element_metadata_response

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
