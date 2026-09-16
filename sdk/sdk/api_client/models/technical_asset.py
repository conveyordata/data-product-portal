from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.technical_asset_status import TechnicalAssetStatus
from ..models.technical_mapping import TechnicalMapping
from ..types import UNSET, Unset

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
        configuration (TechnicalAssetConfiguration): Configuration of the technical asset. The available fields depend
            on `configuration_type`; retrieve them from /v2/plugins/{name}/form.
        platform_id (None | Unset | UUID):
        service_id (None | Unset | UUID):
    """

    id: UUID
    name: str
    namespace: str
    description: str
    status: TechnicalAssetStatus
    technical_mapping: TechnicalMapping
    owner_id: UUID
    configuration: TechnicalAssetConfiguration
    platform_id: None | Unset | UUID = UNSET
    service_id: None | Unset | UUID = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        namespace = self.namespace

        description = self.description

        status = self.status.value

        technical_mapping = self.technical_mapping.value

        owner_id = str(self.owner_id)

        configuration = self.configuration.to_dict()

        platform_id: None | str | Unset
        if isinstance(self.platform_id, Unset):
            platform_id = UNSET
        elif isinstance(self.platform_id, UUID):
            platform_id = str(self.platform_id)
        else:
            platform_id = self.platform_id

        service_id: None | str | Unset
        if isinstance(self.service_id, Unset):
            service_id = UNSET
        elif isinstance(self.service_id, UUID):
            service_id = str(self.service_id)
        else:
            service_id = self.service_id

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
                "configuration": configuration,
            }
        )
        if platform_id is not UNSET:
            field_dict["platform_id"] = platform_id
        if service_id is not UNSET:
            field_dict["service_id"] = service_id

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

        configuration = TechnicalAssetConfiguration.from_dict(d.pop("configuration"))

        def _parse_platform_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                platform_id_type_0 = UUID(data)

                return platform_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        platform_id = _parse_platform_id(d.pop("platform_id", UNSET))

        def _parse_service_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                service_id_type_0 = UUID(data)

                return service_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        service_id = _parse_service_id(d.pop("service_id", UNSET))

        technical_asset = cls(
            id=id,
            name=name,
            namespace=namespace,
            description=description,
            status=status,
            technical_mapping=technical_mapping,
            owner_id=owner_id,
            configuration=configuration,
            platform_id=platform_id,
            service_id=service_id,
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
