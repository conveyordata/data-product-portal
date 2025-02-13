from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_product_status import DataProductStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.business_area import BusinessArea
    from ..models.data_output_get import DataOutputGet
    from ..models.data_product_dataset_association import DataProductDatasetAssociation
    from ..models.data_product_membership import DataProductMembership
    from ..models.tag import Tag


T = TypeVar("T", bound="DataProduct")


@_attrs_define
class DataProduct:
    """
    Attributes:
        name (str):
        external_id (str):
        description (str):
        type_id (UUID):
        id (UUID):
        status (DataProductStatus):
        dataset_links (list['DataProductDatasetAssociation']):
        tags (list['Tag']):
        memberships (list['DataProductMembership']):
        business_area (BusinessArea):
        data_outputs (list['DataOutputGet']):
        about (Union[None, Unset, str]):
    """

    name: str
    external_id: str
    description: str
    type_id: UUID
    id: UUID
    status: DataProductStatus
    dataset_links: list["DataProductDatasetAssociation"]
    tags: list["Tag"]
    memberships: list["DataProductMembership"]
    business_area: "BusinessArea"
    data_outputs: list["DataOutputGet"]
    about: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        external_id = self.external_id

        description = self.description

        type_id = str(self.type_id)

        id = str(self.id)

        status = self.status.value

        dataset_links = []
        for dataset_links_item_data in self.dataset_links:
            dataset_links_item = dataset_links_item_data.to_dict()
            dataset_links.append(dataset_links_item)

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        memberships = []
        for memberships_item_data in self.memberships:
            memberships_item = memberships_item_data.to_dict()
            memberships.append(memberships_item)

        business_area = self.business_area.to_dict()

        data_outputs = []
        for data_outputs_item_data in self.data_outputs:
            data_outputs_item = data_outputs_item_data.to_dict()
            data_outputs.append(data_outputs_item)

        about: Union[None, Unset, str]
        if isinstance(self.about, Unset):
            about = UNSET
        else:
            about = self.about

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "external_id": external_id,
                "description": description,
                "type_id": type_id,
                "id": id,
                "status": status,
                "dataset_links": dataset_links,
                "tags": tags,
                "memberships": memberships,
                "business_area": business_area,
                "data_outputs": data_outputs,
            }
        )
        if about is not UNSET:
            field_dict["about"] = about

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.business_area import BusinessArea
        from ..models.data_output_get import DataOutputGet
        from ..models.data_product_dataset_association import (
            DataProductDatasetAssociation,
        )
        from ..models.data_product_membership import DataProductMembership
        from ..models.tag import Tag

        d = src_dict.copy()
        name = d.pop("name")

        external_id = d.pop("external_id")

        description = d.pop("description")

        type_id = UUID(d.pop("type_id"))

        id = UUID(d.pop("id"))

        status = DataProductStatus(d.pop("status"))

        dataset_links = []
        _dataset_links = d.pop("dataset_links")
        for dataset_links_item_data in _dataset_links:
            dataset_links_item = DataProductDatasetAssociation.from_dict(
                dataset_links_item_data
            )

            dataset_links.append(dataset_links_item)

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        memberships = []
        _memberships = d.pop("memberships")
        for memberships_item_data in _memberships:
            memberships_item = DataProductMembership.from_dict(memberships_item_data)

            memberships.append(memberships_item)

        business_area = BusinessArea.from_dict(d.pop("business_area"))

        data_outputs = []
        _data_outputs = d.pop("data_outputs")
        for data_outputs_item_data in _data_outputs:
            data_outputs_item = DataOutputGet.from_dict(data_outputs_item_data)

            data_outputs.append(data_outputs_item)

        def _parse_about(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        about = _parse_about(d.pop("about", UNSET))

        data_product = cls(
            name=name,
            external_id=external_id,
            description=description,
            type_id=type_id,
            id=id,
            status=status,
            dataset_links=dataset_links,
            tags=tags,
            memberships=memberships,
            business_area=business_area,
            data_outputs=data_outputs,
            about=about,
        )

        data_product.additional_properties = d
        return data_product

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
