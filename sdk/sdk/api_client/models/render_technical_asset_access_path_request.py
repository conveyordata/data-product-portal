from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.render_technical_asset_access_path_request_configuration import (
        RenderTechnicalAssetAccessPathRequestConfiguration,
    )


T = TypeVar("T", bound="RenderTechnicalAssetAccessPathRequest")


@_attrs_define
class RenderTechnicalAssetAccessPathRequest:
    """
    Attributes:
        platform_id (UUID):
        service_id (UUID):
        configuration (RenderTechnicalAssetAccessPathRequestConfiguration): Configuration of the technical asset. The
            available fields depend on `name`; retrieve them from /v2/plugins/{name}/form.
    """

    platform_id: UUID
    service_id: UUID
    configuration: RenderTechnicalAssetAccessPathRequestConfiguration
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        platform_id = str(self.platform_id)

        service_id = str(self.service_id)

        configuration = self.configuration.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "platform_id": platform_id,
                "service_id": service_id,
                "configuration": configuration,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.render_technical_asset_access_path_request_configuration import (
            RenderTechnicalAssetAccessPathRequestConfiguration,
        )

        d = dict(src_dict)
        platform_id = UUID(d.pop("platform_id"))

        service_id = UUID(d.pop("service_id"))

        configuration = RenderTechnicalAssetAccessPathRequestConfiguration.from_dict(
            d.pop("configuration")
        )

        render_technical_asset_access_path_request = cls(
            platform_id=platform_id,
            service_id=service_id,
            configuration=configuration,
        )

        render_technical_asset_access_path_request.additional_properties = d
        return render_technical_asset_access_path_request

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
