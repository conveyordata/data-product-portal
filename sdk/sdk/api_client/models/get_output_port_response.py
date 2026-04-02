from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.output_port_access_type import OutputPortAccessType
from ..models.output_port_status import OutputPortStatus

if TYPE_CHECKING:
    from ..models.data_product_life_cycle import DataProductLifeCycle
    from ..models.domain import Domain
    from ..models.output_port_setting_value import OutputPortSettingValue
    from ..models.tag import Tag
    from ..models.technical_asset_link import TechnicalAssetLink


T = TypeVar("T", bound="GetOutputPortResponse")


@_attrs_define
class GetOutputPortResponse:
    """
    Attributes:
        id (UUID):
        namespace (str):
        name (str):
        description (str):
        status (OutputPortStatus):
        usage (None | str):
        access_type (OutputPortAccessType):
        data_product_id (UUID):
        tags (list[Tag]):
        domain (Domain):
        lifecycle (DataProductLifeCycle | None):
        about (None | str):
        rolled_up_tags (list[Tag]):
        data_product_settings (list[OutputPortSettingValue]):
        technical_asset_links (list[TechnicalAssetLink]):
    """

    id: UUID
    namespace: str
    name: str
    description: str
    status: OutputPortStatus
    usage: None | str
    access_type: OutputPortAccessType
    data_product_id: UUID
    tags: list[Tag]
    domain: Domain
    lifecycle: DataProductLifeCycle | None
    about: None | str
    rolled_up_tags: list[Tag]
    data_product_settings: list[OutputPortSettingValue]
    technical_asset_links: list[TechnicalAssetLink]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.data_product_life_cycle import DataProductLifeCycle

        id = str(self.id)

        namespace = self.namespace

        name = self.name

        description = self.description

        status = self.status.value

        usage: None | str
        usage = self.usage

        access_type = self.access_type.value

        data_product_id = str(self.data_product_id)

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        domain = self.domain.to_dict()

        lifecycle: dict[str, Any] | None
        if isinstance(self.lifecycle, DataProductLifeCycle):
            lifecycle = self.lifecycle.to_dict()
        else:
            lifecycle = self.lifecycle

        about: None | str
        about = self.about

        rolled_up_tags = []
        for rolled_up_tags_item_data in self.rolled_up_tags:
            rolled_up_tags_item = rolled_up_tags_item_data.to_dict()
            rolled_up_tags.append(rolled_up_tags_item)

        data_product_settings = []
        for data_product_settings_item_data in self.data_product_settings:
            data_product_settings_item = data_product_settings_item_data.to_dict()
            data_product_settings.append(data_product_settings_item)

        technical_asset_links = []
        for technical_asset_links_item_data in self.technical_asset_links:
            technical_asset_links_item = technical_asset_links_item_data.to_dict()
            technical_asset_links.append(technical_asset_links_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "namespace": namespace,
                "name": name,
                "description": description,
                "status": status,
                "usage": usage,
                "access_type": access_type,
                "data_product_id": data_product_id,
                "tags": tags,
                "domain": domain,
                "lifecycle": lifecycle,
                "about": about,
                "rolled_up_tags": rolled_up_tags,
                "data_product_settings": data_product_settings,
                "technical_asset_links": technical_asset_links,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_product_life_cycle import DataProductLifeCycle
        from ..models.domain import Domain
        from ..models.output_port_setting_value import OutputPortSettingValue
        from ..models.tag import Tag
        from ..models.technical_asset_link import TechnicalAssetLink

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        namespace = d.pop("namespace")

        name = d.pop("name")

        description = d.pop("description")

        status = OutputPortStatus(d.pop("status"))

        def _parse_usage(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        usage = _parse_usage(d.pop("usage"))

        access_type = OutputPortAccessType(d.pop("access_type"))

        data_product_id = UUID(d.pop("data_product_id"))

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        domain = Domain.from_dict(d.pop("domain"))

        def _parse_lifecycle(data: object) -> DataProductLifeCycle | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                lifecycle_type_0 = DataProductLifeCycle.from_dict(data)

                return lifecycle_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DataProductLifeCycle | None, data)

        lifecycle = _parse_lifecycle(d.pop("lifecycle"))

        def _parse_about(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        about = _parse_about(d.pop("about"))

        rolled_up_tags = []
        _rolled_up_tags = d.pop("rolled_up_tags")
        for rolled_up_tags_item_data in _rolled_up_tags:
            rolled_up_tags_item = Tag.from_dict(rolled_up_tags_item_data)

            rolled_up_tags.append(rolled_up_tags_item)

        data_product_settings = []
        _data_product_settings = d.pop("data_product_settings")
        for data_product_settings_item_data in _data_product_settings:
            data_product_settings_item = OutputPortSettingValue.from_dict(
                data_product_settings_item_data
            )

            data_product_settings.append(data_product_settings_item)

        technical_asset_links = []
        _technical_asset_links = d.pop("technical_asset_links")
        for technical_asset_links_item_data in _technical_asset_links:
            technical_asset_links_item = TechnicalAssetLink.from_dict(
                technical_asset_links_item_data
            )

            technical_asset_links.append(technical_asset_links_item)

        get_output_port_response = cls(
            id=id,
            namespace=namespace,
            name=name,
            description=description,
            status=status,
            usage=usage,
            access_type=access_type,
            data_product_id=data_product_id,
            tags=tags,
            domain=domain,
            lifecycle=lifecycle,
            about=about,
            rolled_up_tags=rolled_up_tags,
            data_product_settings=data_product_settings,
            technical_asset_links=technical_asset_links,
        )

        get_output_port_response.additional_properties = d
        return get_output_port_response

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
