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
    from ..models.access_mode import AccessMode
    from ..models.data_product import DataProduct
    from ..models.get_technical_assets_response_item_configuration import (
        GetTechnicalAssetsResponseItemConfiguration,
    )
    from ..models.output_port_link import OutputPortLink
    from ..models.tag import Tag
    from ..models.technical_info import TechnicalInfo


T = TypeVar("T", bound="GetTechnicalAssetsResponseItem")


@_attrs_define
class GetTechnicalAssetsResponseItem:
    """
    Attributes:
        id (UUID):
        name (str):
        description (str):
        namespace (str):
        owner_id (UUID):
        status (TechnicalAssetStatus):
        technical_mapping (TechnicalMapping):
        access_modes (list[AccessMode]):
        configuration (GetTechnicalAssetsResponseItemConfiguration): Configuration of the technical asset. The available
            fields depend on `configuration_type`; retrieve them from /v2/plugins/{name}/form.
        owner (DataProduct):
        output_port_links (list[OutputPortLink]):
        tags (list[Tag]):
        source_aligned (bool): DEPRECATED: Use 'technical_mapping' instead. This field will be removed in a future
            version.
        result_string (str):
        technical_info (list[TechnicalInfo]):
        platform_id (None | Unset | UUID):
        service_id (None | Unset | UUID):
    """

    id: UUID
    name: str
    description: str
    namespace: str
    owner_id: UUID
    status: TechnicalAssetStatus
    technical_mapping: TechnicalMapping
    access_modes: list[AccessMode]
    configuration: GetTechnicalAssetsResponseItemConfiguration
    owner: DataProduct
    output_port_links: list[OutputPortLink]
    tags: list[Tag]
    source_aligned: bool
    result_string: str
    technical_info: list[TechnicalInfo]
    platform_id: None | Unset | UUID = UNSET
    service_id: None | Unset | UUID = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        description = self.description

        namespace = self.namespace

        owner_id = str(self.owner_id)

        status = self.status.value

        technical_mapping = self.technical_mapping.value

        access_modes = []
        for access_modes_item_data in self.access_modes:
            access_modes_item = access_modes_item_data.to_dict()
            access_modes.append(access_modes_item)

        configuration = self.configuration.to_dict()

        owner = self.owner.to_dict()

        output_port_links = []
        for output_port_links_item_data in self.output_port_links:
            output_port_links_item = output_port_links_item_data.to_dict()
            output_port_links.append(output_port_links_item)

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        source_aligned = self.source_aligned

        result_string = self.result_string

        technical_info = []
        for technical_info_item_data in self.technical_info:
            technical_info_item = technical_info_item_data.to_dict()
            technical_info.append(technical_info_item)

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
                "description": description,
                "namespace": namespace,
                "owner_id": owner_id,
                "status": status,
                "technical_mapping": technical_mapping,
                "access_modes": access_modes,
                "configuration": configuration,
                "owner": owner,
                "output_port_links": output_port_links,
                "tags": tags,
                "sourceAligned": source_aligned,
                "result_string": result_string,
                "technical_info": technical_info,
            }
        )
        if platform_id is not UNSET:
            field_dict["platform_id"] = platform_id
        if service_id is not UNSET:
            field_dict["service_id"] = service_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_mode import AccessMode
        from ..models.data_product import DataProduct
        from ..models.get_technical_assets_response_item_configuration import (
            GetTechnicalAssetsResponseItemConfiguration,
        )
        from ..models.output_port_link import OutputPortLink
        from ..models.tag import Tag
        from ..models.technical_info import TechnicalInfo

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        description = d.pop("description")

        namespace = d.pop("namespace")

        owner_id = UUID(d.pop("owner_id"))

        status = TechnicalAssetStatus(d.pop("status"))

        technical_mapping = TechnicalMapping(d.pop("technical_mapping"))

        access_modes = []
        _access_modes = d.pop("access_modes")
        for access_modes_item_data in _access_modes:
            access_modes_item = AccessMode.from_dict(access_modes_item_data)

            access_modes.append(access_modes_item)

        configuration = GetTechnicalAssetsResponseItemConfiguration.from_dict(
            d.pop("configuration")
        )

        owner = DataProduct.from_dict(d.pop("owner"))

        output_port_links = []
        _output_port_links = d.pop("output_port_links")
        for output_port_links_item_data in _output_port_links:
            output_port_links_item = OutputPortLink.from_dict(
                output_port_links_item_data
            )

            output_port_links.append(output_port_links_item)

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        source_aligned = d.pop("sourceAligned")

        result_string = d.pop("result_string")

        technical_info = []
        _technical_info = d.pop("technical_info")
        for technical_info_item_data in _technical_info:
            technical_info_item = TechnicalInfo.from_dict(technical_info_item_data)

            technical_info.append(technical_info_item)

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

        get_technical_assets_response_item = cls(
            id=id,
            name=name,
            description=description,
            namespace=namespace,
            owner_id=owner_id,
            status=status,
            technical_mapping=technical_mapping,
            access_modes=access_modes,
            configuration=configuration,
            owner=owner,
            output_port_links=output_port_links,
            tags=tags,
            source_aligned=source_aligned,
            result_string=result_string,
            technical_info=technical_info,
            platform_id=platform_id,
            service_id=service_id,
        )

        get_technical_assets_response_item.additional_properties = d
        return get_technical_assets_response_item

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
