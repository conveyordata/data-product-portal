from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.technical_mapping import TechnicalMapping

if TYPE_CHECKING:
    from ..models.render_technical_asset_access_path_request_configuration import (
        RenderTechnicalAssetAccessPathRequestConfiguration,
    )


T = TypeVar("T", bound="RenderTechnicalAssetAccessPathRequest")


@_attrs_define
class RenderTechnicalAssetAccessPathRequest:
    """
    Attributes:
        data_product_id (UUID):
        namespace (str):
        technical_mapping (TechnicalMapping):
        configuration (RenderTechnicalAssetAccessPathRequestConfiguration): Configuration of the technical asset. The
            available fields depend on `name`; retrieve them from /v2/plugins/{name}/form.
    """

    data_product_id: UUID
    namespace: str
    technical_mapping: TechnicalMapping
    configuration: RenderTechnicalAssetAccessPathRequestConfiguration
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_product_id = str(self.data_product_id)

        namespace = self.namespace

        technical_mapping = self.technical_mapping.value

        configuration = self.configuration.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_product_id": data_product_id,
                "namespace": namespace,
                "technical_mapping": technical_mapping,
                "configuration": configuration,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.render_technical_asset_access_path_request_configuration import (
            RenderTechnicalAssetAccessPathRequestConfiguration,  # noqa: PLC0415
        )

        d = dict(src_dict)
        data_product_id = UUID(d.pop("data_product_id"))

        namespace = d.pop("namespace")

        technical_mapping = TechnicalMapping(d.pop("technical_mapping"))

        configuration = RenderTechnicalAssetAccessPathRequestConfiguration.from_dict(
            d.pop("configuration")
        )

        render_technical_asset_access_path_request = cls(
            data_product_id=data_product_id,
            namespace=namespace,
            technical_mapping=technical_mapping,
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
