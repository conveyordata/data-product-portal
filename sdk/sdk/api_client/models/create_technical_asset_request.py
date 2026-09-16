from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.technical_mapping import TechnicalMapping
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_technical_asset_request_configuration import (
        CreateTechnicalAssetRequestConfiguration,
    )


T = TypeVar("T", bound="CreateTechnicalAssetRequest")


@_attrs_define
class CreateTechnicalAssetRequest:
    """
    Attributes:
        name (str):
        description (str):
        namespace (str):
        configuration (CreateTechnicalAssetRequestConfiguration): Configuration of the technical asset. The available
            fields depend on `configuration_type`; retrieve them from /v2/plugins/{name}/form.
        tag_ids (list[UUID]):
        platform_id (None | Unset | UUID):
        service_id (None | Unset | UUID):
        source_aligned (bool | None | Unset): DEPRECATED: Use 'technical_mapping' instead. This field will be removed in
            a future version.
        technical_mapping (None | TechnicalMapping | Unset):
        access_mode_ids (list[UUID] | Unset):
    """

    name: str
    description: str
    namespace: str
    configuration: CreateTechnicalAssetRequestConfiguration
    tag_ids: list[UUID]
    platform_id: None | Unset | UUID = UNSET
    service_id: None | Unset | UUID = UNSET
    source_aligned: bool | None | Unset = UNSET
    technical_mapping: None | TechnicalMapping | Unset = UNSET
    access_mode_ids: list[UUID] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        namespace = self.namespace

        configuration = self.configuration.to_dict()

        tag_ids = []
        for tag_ids_item_data in self.tag_ids:
            tag_ids_item = str(tag_ids_item_data)
            tag_ids.append(tag_ids_item)

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

        source_aligned: bool | None | Unset
        if isinstance(self.source_aligned, Unset):
            source_aligned = UNSET
        else:
            source_aligned = self.source_aligned

        technical_mapping: None | str | Unset
        if isinstance(self.technical_mapping, Unset):
            technical_mapping = UNSET
        elif isinstance(self.technical_mapping, TechnicalMapping):
            technical_mapping = self.technical_mapping.value
        else:
            technical_mapping = self.technical_mapping

        access_mode_ids: list[str] | Unset = UNSET
        if not isinstance(self.access_mode_ids, Unset):
            access_mode_ids = []
            for access_mode_ids_item_data in self.access_mode_ids:
                access_mode_ids_item = str(access_mode_ids_item_data)
                access_mode_ids.append(access_mode_ids_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "namespace": namespace,
                "configuration": configuration,
                "tag_ids": tag_ids,
            }
        )
        if platform_id is not UNSET:
            field_dict["platform_id"] = platform_id
        if service_id is not UNSET:
            field_dict["service_id"] = service_id
        if source_aligned is not UNSET:
            field_dict["sourceAligned"] = source_aligned
        if technical_mapping is not UNSET:
            field_dict["technical_mapping"] = technical_mapping
        if access_mode_ids is not UNSET:
            field_dict["access_mode_ids"] = access_mode_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_technical_asset_request_configuration import (
            CreateTechnicalAssetRequestConfiguration,
        )

        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        namespace = d.pop("namespace")

        configuration = CreateTechnicalAssetRequestConfiguration.from_dict(
            d.pop("configuration")
        )

        tag_ids = []
        _tag_ids = d.pop("tag_ids")
        for tag_ids_item_data in _tag_ids:
            tag_ids_item = UUID(tag_ids_item_data)

            tag_ids.append(tag_ids_item)

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

        def _parse_source_aligned(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        source_aligned = _parse_source_aligned(d.pop("sourceAligned", UNSET))

        def _parse_technical_mapping(data: object) -> None | TechnicalMapping | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                technical_mapping_type_0 = TechnicalMapping(data)

                return technical_mapping_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TechnicalMapping | Unset, data)

        technical_mapping = _parse_technical_mapping(d.pop("technical_mapping", UNSET))

        _access_mode_ids = d.pop("access_mode_ids", UNSET)
        access_mode_ids: list[UUID] | Unset = UNSET
        if _access_mode_ids is not UNSET:
            access_mode_ids = []
            for access_mode_ids_item_data in _access_mode_ids:
                access_mode_ids_item = UUID(access_mode_ids_item_data)

                access_mode_ids.append(access_mode_ids_item)

        create_technical_asset_request = cls(
            name=name,
            description=description,
            namespace=namespace,
            configuration=configuration,
            tag_ids=tag_ids,
            platform_id=platform_id,
            service_id=service_id,
            source_aligned=source_aligned,
            technical_mapping=technical_mapping,
            access_mode_ids=access_mode_ids,
        )

        create_technical_asset_request.additional_properties = d
        return create_technical_asset_request

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
