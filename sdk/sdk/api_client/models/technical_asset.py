from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.technical_asset_status import TechnicalAssetStatus
from ..models.technical_mapping import TechnicalMapping

if TYPE_CHECKING:
    from ..models.technical_asset_configuration import TechnicalAssetConfiguration


T = TypeVar("T", bound="TechnicalAsset")


@_attrs_define
class TechnicalAsset:
    """
    Attributes:
        id (UUID):
        name (str):
        namespace (str):
        description (str):
        status (TechnicalAssetStatus):
        technical_mapping (TechnicalMapping):
        owner_id (UUID):
        platform_id (UUID):
        service_id (UUID):
        configuration (TechnicalAssetConfiguration): Configuration of the technical asset. The available fields depend
            on `configuration_type`; retrieve them from /v2/plugins/{name}/form.
    """

    id: UUID
    name: str
    namespace: str
    description: str
    status: TechnicalAssetStatus
    technical_mapping: TechnicalMapping
    owner_id: UUID
    platform_id: UUID
    service_id: UUID
    configuration: TechnicalAssetConfiguration
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        namespace = self.namespace

        description = self.description

        status = self.status.value

        technical_mapping = self.technical_mapping.value

        owner_id = str(self.owner_id)

        platform_id = str(self.platform_id)

        service_id = str(self.service_id)

        configuration = self.configuration.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "namespace": namespace,
                "description": description,
                "status": status,
                "technical_mapping": technical_mapping,
                "owner_id": owner_id,
                "platform_id": platform_id,
                "service_id": service_id,
                "configuration": configuration,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.technical_asset_configuration import TechnicalAssetConfiguration

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        namespace = d.pop("namespace")

        description = d.pop("description")

        status = TechnicalAssetStatus(d.pop("status"))

        technical_mapping = TechnicalMapping(d.pop("technical_mapping"))

        owner_id = UUID(d.pop("owner_id"))

        platform_id = UUID(d.pop("platform_id"))

        service_id = UUID(d.pop("service_id"))

        configuration = TechnicalAssetConfiguration.from_dict(d.pop("configuration"))

        technical_asset = cls(
            id=id,
            name=name,
            namespace=namespace,
            description=description,
            status=status,
            technical_mapping=technical_mapping,
            owner_id=owner_id,
            platform_id=platform_id,
            service_id=service_id,
            configuration=configuration,
        )

        technical_asset.additional_properties = d
        return technical_asset

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
