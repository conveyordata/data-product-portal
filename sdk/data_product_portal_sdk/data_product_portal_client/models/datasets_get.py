from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.dataset_access_type import DatasetAccessType
from ..models.dataset_status import DatasetStatus

if TYPE_CHECKING:
    from ..models.business_area import BusinessArea
    from ..models.data_output_link import DataOutputLink
    from ..models.data_product_life_cycle import DataProductLifeCycle
    from ..models.data_product_setting_value import DataProductSettingValue
    from ..models.tag import Tag
    from ..models.user import User


T = TypeVar("T", bound="DatasetsGet")


@_attrs_define
class DatasetsGet:
    """
    Attributes:
        id (UUID):
        external_id (str):
        name (str):
        description (str):
        owners (list['User']):
        lifecycle (Union['DataProductLifeCycle', None]):
        status (DatasetStatus):
        tags (list['Tag']):
        business_area (BusinessArea):
        access_type (DatasetAccessType):
        data_output_links (list['DataOutputLink']):
        data_product_settings (list['DataProductSettingValue']):
        data_product_count (int):
    """

    id: UUID
    external_id: str
    name: str
    description: str
    owners: list["User"]
    lifecycle: Union["DataProductLifeCycle", None]
    status: DatasetStatus
    tags: list["Tag"]
    business_area: "BusinessArea"
    access_type: DatasetAccessType
    data_output_links: list["DataOutputLink"]
    data_product_settings: list["DataProductSettingValue"]
    data_product_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.data_product_life_cycle import DataProductLifeCycle

        id = str(self.id)

        external_id = self.external_id

        name = self.name

        description = self.description

        owners = []
        for owners_item_data in self.owners:
            owners_item = owners_item_data.to_dict()
            owners.append(owners_item)

        lifecycle: Union[None, dict[str, Any]]
        if isinstance(self.lifecycle, DataProductLifeCycle):
            lifecycle = self.lifecycle.to_dict()
        else:
            lifecycle = self.lifecycle

        status = self.status.value

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        business_area = self.business_area.to_dict()

        access_type = self.access_type.value

        data_output_links = []
        for data_output_links_item_data in self.data_output_links:
            data_output_links_item = data_output_links_item_data.to_dict()
            data_output_links.append(data_output_links_item)

        data_product_settings = []
        for data_product_settings_item_data in self.data_product_settings:
            data_product_settings_item = data_product_settings_item_data.to_dict()
            data_product_settings.append(data_product_settings_item)

        data_product_count = self.data_product_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "external_id": external_id,
                "name": name,
                "description": description,
                "owners": owners,
                "lifecycle": lifecycle,
                "status": status,
                "tags": tags,
                "business_area": business_area,
                "access_type": access_type,
                "data_output_links": data_output_links,
                "data_product_settings": data_product_settings,
                "data_product_count": data_product_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.business_area import BusinessArea
        from ..models.data_output_link import DataOutputLink
        from ..models.data_product_life_cycle import DataProductLifeCycle
        from ..models.data_product_setting_value import DataProductSettingValue
        from ..models.tag import Tag
        from ..models.user import User

        d = src_dict.copy()
        id = UUID(d.pop("id"))

        external_id = d.pop("external_id")

        name = d.pop("name")

        description = d.pop("description")

        owners = []
        _owners = d.pop("owners")
        for owners_item_data in _owners:
            owners_item = User.from_dict(owners_item_data)

            owners.append(owners_item)

        def _parse_lifecycle(data: object) -> Union["DataProductLifeCycle", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                lifecycle_type_0 = DataProductLifeCycle.from_dict(data)

                return lifecycle_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DataProductLifeCycle", None], data)

        lifecycle = _parse_lifecycle(d.pop("lifecycle"))

        status = DatasetStatus(d.pop("status"))

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        business_area = BusinessArea.from_dict(d.pop("business_area"))

        access_type = DatasetAccessType(d.pop("access_type"))

        data_output_links = []
        _data_output_links = d.pop("data_output_links")
        for data_output_links_item_data in _data_output_links:
            data_output_links_item = DataOutputLink.from_dict(
                data_output_links_item_data
            )

            data_output_links.append(data_output_links_item)

        data_product_settings = []
        _data_product_settings = d.pop("data_product_settings")
        for data_product_settings_item_data in _data_product_settings:
            data_product_settings_item = DataProductSettingValue.from_dict(
                data_product_settings_item_data
            )

            data_product_settings.append(data_product_settings_item)

        data_product_count = d.pop("data_product_count")

        datasets_get = cls(
            id=id,
            external_id=external_id,
            name=name,
            description=description,
            owners=owners,
            lifecycle=lifecycle,
            status=status,
            tags=tags,
            business_area=business_area,
            access_type=access_type,
            data_output_links=data_output_links,
            data_product_settings=data_product_settings,
            data_product_count=data_product_count,
        )

        datasets_get.additional_properties = d
        return datasets_get

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
