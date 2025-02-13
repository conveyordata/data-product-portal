from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_product_membership_create import DataProductMembershipCreate


T = TypeVar("T", bound="DataProductUpdate")


@_attrs_define
class DataProductUpdate:
    """
    Attributes:
        name (str):
        external_id (str):
        description (str):
        type_id (UUID):
        memberships (list['DataProductMembershipCreate']):
        business_area_id (UUID):
        tag_ids (list[UUID]):
        lifecycle_id (UUID):
        about (Union[None, Unset, str]):
    """

    name: str
    external_id: str
    description: str
    type_id: UUID
    memberships: list["DataProductMembershipCreate"]
    business_area_id: UUID
    tag_ids: list[UUID]
    lifecycle_id: UUID
    about: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        external_id = self.external_id

        description = self.description

        type_id = str(self.type_id)

        memberships = []
        for memberships_item_data in self.memberships:
            memberships_item = memberships_item_data.to_dict()
            memberships.append(memberships_item)

        business_area_id = str(self.business_area_id)

        tag_ids = []
        for tag_ids_item_data in self.tag_ids:
            tag_ids_item = str(tag_ids_item_data)
            tag_ids.append(tag_ids_item)

        lifecycle_id = str(self.lifecycle_id)

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
                "memberships": memberships,
                "business_area_id": business_area_id,
                "tag_ids": tag_ids,
                "lifecycle_id": lifecycle_id,
            }
        )
        if about is not UNSET:
            field_dict["about"] = about

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.data_product_membership_create import DataProductMembershipCreate

        d = src_dict.copy()
        name = d.pop("name")

        external_id = d.pop("external_id")

        description = d.pop("description")

        type_id = UUID(d.pop("type_id"))

        memberships = []
        _memberships = d.pop("memberships")
        for memberships_item_data in _memberships:
            memberships_item = DataProductMembershipCreate.from_dict(
                memberships_item_data
            )

            memberships.append(memberships_item)

        business_area_id = UUID(d.pop("business_area_id"))

        tag_ids = []
        _tag_ids = d.pop("tag_ids")
        for tag_ids_item_data in _tag_ids:
            tag_ids_item = UUID(tag_ids_item_data)

            tag_ids.append(tag_ids_item)

        lifecycle_id = UUID(d.pop("lifecycle_id"))

        def _parse_about(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        about = _parse_about(d.pop("about", UNSET))

        data_product_update = cls(
            name=name,
            external_id=external_id,
            description=description,
            type_id=type_id,
            memberships=memberships,
            business_area_id=business_area_id,
            tag_ids=tag_ids,
            lifecycle_id=lifecycle_id,
            about=about,
        )

        data_product_update.additional_properties = d
        return data_product_update

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
