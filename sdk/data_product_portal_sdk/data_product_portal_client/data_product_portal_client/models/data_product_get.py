from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_product_status import DataProductStatus

if TYPE_CHECKING:
    from ..models.business_area import BusinessArea
    from ..models.data_output_get import DataOutputGet
    from ..models.data_product_life_cycle import DataProductLifeCycle
    from ..models.data_product_membership_get import DataProductMembershipGet
    from ..models.data_product_setting_value import DataProductSettingValue
    from ..models.data_product_type import DataProductType
    from ..models.dataset_data_product_link import DatasetDataProductLink
    from ..models.tag import Tag


T = TypeVar("T", bound="DataProductGet")


@_attrs_define
class DataProductGet:
    """
    Attributes:
        id (UUID):
        name (str):
        description (str):
        about (Union[None, str]):
        external_id (str):
        tags (list['Tag']):
        status (DataProductStatus):
        lifecycle (Union['DataProductLifeCycle', None]):
        dataset_links (list['DatasetDataProductLink']):
        memberships (list['DataProductMembershipGet']):
        type_ (DataProductType):
        business_area (BusinessArea):
        data_outputs (list['DataOutputGet']):
        data_product_settings (list['DataProductSettingValue']):
    """

    id: UUID
    name: str
    description: str
    about: Union[None, str]
    external_id: str
    tags: list["Tag"]
    status: DataProductStatus
    lifecycle: Union["DataProductLifeCycle", None]
    dataset_links: list["DatasetDataProductLink"]
    memberships: list["DataProductMembershipGet"]
    type_: "DataProductType"
    business_area: "BusinessArea"
    data_outputs: list["DataOutputGet"]
    data_product_settings: list["DataProductSettingValue"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.data_product_life_cycle import DataProductLifeCycle

        id = str(self.id)

        name = self.name

        description = self.description

        about: Union[None, str]
        about = self.about

        external_id = self.external_id

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        status = self.status.value

        lifecycle: Union[None, dict[str, Any]]
        if isinstance(self.lifecycle, DataProductLifeCycle):
            lifecycle = self.lifecycle.to_dict()
        else:
            lifecycle = self.lifecycle

        dataset_links = []
        for dataset_links_item_data in self.dataset_links:
            dataset_links_item = dataset_links_item_data.to_dict()
            dataset_links.append(dataset_links_item)

        memberships = []
        for memberships_item_data in self.memberships:
            memberships_item = memberships_item_data.to_dict()
            memberships.append(memberships_item)

        type_ = self.type_.to_dict()

        business_area = self.business_area.to_dict()

        data_outputs = []
        for data_outputs_item_data in self.data_outputs:
            data_outputs_item = data_outputs_item_data.to_dict()
            data_outputs.append(data_outputs_item)

        data_product_settings = []
        for data_product_settings_item_data in self.data_product_settings:
            data_product_settings_item = data_product_settings_item_data.to_dict()
            data_product_settings.append(data_product_settings_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "about": about,
                "external_id": external_id,
                "tags": tags,
                "status": status,
                "lifecycle": lifecycle,
                "dataset_links": dataset_links,
                "memberships": memberships,
                "type": type_,
                "business_area": business_area,
                "data_outputs": data_outputs,
                "data_product_settings": data_product_settings,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.business_area import BusinessArea
        from ..models.data_output_get import DataOutputGet
        from ..models.data_product_life_cycle import DataProductLifeCycle
        from ..models.data_product_membership_get import DataProductMembershipGet
        from ..models.data_product_setting_value import DataProductSettingValue
        from ..models.data_product_type import DataProductType
        from ..models.dataset_data_product_link import DatasetDataProductLink
        from ..models.tag import Tag

        d = src_dict.copy()
        id = UUID(d.pop("id"))

        name = d.pop("name")

        description = d.pop("description")

        def _parse_about(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        about = _parse_about(d.pop("about"))

        external_id = d.pop("external_id")

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        status = DataProductStatus(d.pop("status"))

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

        dataset_links = []
        _dataset_links = d.pop("dataset_links")
        for dataset_links_item_data in _dataset_links:
            dataset_links_item = DatasetDataProductLink.from_dict(
                dataset_links_item_data
            )

            dataset_links.append(dataset_links_item)

        memberships = []
        _memberships = d.pop("memberships")
        for memberships_item_data in _memberships:
            memberships_item = DataProductMembershipGet.from_dict(memberships_item_data)

            memberships.append(memberships_item)

        type_ = DataProductType.from_dict(d.pop("type"))

        business_area = BusinessArea.from_dict(d.pop("business_area"))

        data_outputs = []
        _data_outputs = d.pop("data_outputs")
        for data_outputs_item_data in _data_outputs:
            data_outputs_item = DataOutputGet.from_dict(data_outputs_item_data)

            data_outputs.append(data_outputs_item)

        data_product_settings = []
        _data_product_settings = d.pop("data_product_settings")
        for data_product_settings_item_data in _data_product_settings:
            data_product_settings_item = DataProductSettingValue.from_dict(
                data_product_settings_item_data
            )

            data_product_settings.append(data_product_settings_item)

        data_product_get = cls(
            id=id,
            name=name,
            description=description,
            about=about,
            external_id=external_id,
            tags=tags,
            status=status,
            lifecycle=lifecycle,
            dataset_links=dataset_links,
            memberships=memberships,
            type_=type_,
            business_area=business_area,
            data_outputs=data_outputs,
            data_product_settings=data_product_settings,
        )

        data_product_get.additional_properties = d
        return data_product_get

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
