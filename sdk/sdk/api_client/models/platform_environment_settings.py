from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.platform_environment_settings_settings import (
        PlatformEnvironmentSettingsSettings,
    )


T = TypeVar("T", bound="PlatformEnvironmentSettings")


@_attrs_define
class PlatformEnvironmentSettings:
    """
    Attributes:
        platform_key (str):
        environment_id (UUID):
        settings (PlatformEnvironmentSettingsSettings):
    """

    platform_key: str
    environment_id: UUID
    settings: PlatformEnvironmentSettingsSettings
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        platform_key = self.platform_key

        environment_id = str(self.environment_id)

        settings = self.settings.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "platform_key": platform_key,
                "environment_id": environment_id,
                "settings": settings,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.platform_environment_settings_settings import (
            PlatformEnvironmentSettingsSettings,  # noqa: PLC0415
        )

        d = dict(src_dict)
        platform_key = d.pop("platform_key")

        environment_id = UUID(d.pop("environment_id"))

        settings = PlatformEnvironmentSettingsSettings.from_dict(d.pop("settings"))

        platform_environment_settings = cls(
            platform_key=platform_key,
            environment_id=environment_id,
            settings=settings,
        )

        platform_environment_settings.additional_properties = d
        return platform_environment_settings

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
