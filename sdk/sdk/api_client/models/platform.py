from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.platform_settings_schema import PlatformSettingsSchema
    from ..models.platform_type import PlatformType


T = TypeVar("T", bound="Platform")


@_attrs_define
class Platform:
    """
    Attributes:
        key (str):
        display_name (str):
        icon_name (str):
        icon_data_uri (None | str):
        has_environments (bool):
        settings_schema (PlatformSettingsSchema):
        types (list[PlatformType]):
    """

    key: str
    display_name: str
    icon_name: str
    icon_data_uri: None | str
    has_environments: bool
    settings_schema: PlatformSettingsSchema
    types: list[PlatformType]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        key = self.key

        display_name = self.display_name

        icon_name = self.icon_name

        icon_data_uri: None | str
        icon_data_uri = self.icon_data_uri

        has_environments = self.has_environments

        settings_schema = self.settings_schema.to_dict()

        types = []
        for types_item_data in self.types:
            types_item = types_item_data.to_dict()
            types.append(types_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "display_name": display_name,
                "icon_name": icon_name,
                "icon_data_uri": icon_data_uri,
                "has_environments": has_environments,
                "settings_schema": settings_schema,
                "types": types,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.platform_settings_schema import (
            PlatformSettingsSchema,  # noqa: PLC0415
        )
        from ..models.platform_type import PlatformType  # noqa: PLC0415

        d = dict(src_dict)
        key = d.pop("key")

        display_name = d.pop("display_name")

        icon_name = d.pop("icon_name")

        def _parse_icon_data_uri(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        icon_data_uri = _parse_icon_data_uri(d.pop("icon_data_uri"))

        has_environments = d.pop("has_environments")

        settings_schema = PlatformSettingsSchema.from_dict(d.pop("settings_schema"))

        types = []
        _types = d.pop("types")
        for types_item_data in _types:
            types_item = PlatformType.from_dict(types_item_data)

            types.append(types_item)

        platform = cls(
            key=key,
            display_name=display_name,
            icon_name=icon_name,
            icon_data_uri=icon_data_uri,
            has_environments=has_environments,
            settings_schema=settings_schema,
            types=types,
        )

        platform.additional_properties = d
        return platform

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
