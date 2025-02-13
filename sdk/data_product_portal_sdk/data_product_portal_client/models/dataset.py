from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.dataset_access_type import DatasetAccessType
from ..models.dataset_status import DatasetStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.business_area import BusinessArea
    from ..models.tag import Tag
    from ..models.user import User


T = TypeVar("T", bound="Dataset")


@_attrs_define
class Dataset:
    """
    Attributes:
        name (str):
        external_id (str):
        description (str):
        access_type (DatasetAccessType):
        id (UUID):
        owners (list['User']):
        status (DatasetStatus):
        business_area (BusinessArea):
        tags (list['Tag']):
        about (Union[None, Unset, str]):
        lifecycle_id (Union[None, UUID, Unset]):
    """

    name: str
    external_id: str
    description: str
    access_type: DatasetAccessType
    id: UUID
    owners: list["User"]
    status: DatasetStatus
    business_area: "BusinessArea"
    tags: list["Tag"]
    about: Union[None, Unset, str] = UNSET
    lifecycle_id: Union[None, UUID, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        external_id = self.external_id

        description = self.description

        access_type = self.access_type.value

        id = str(self.id)

        owners = []
        for owners_item_data in self.owners:
            owners_item = owners_item_data.to_dict()
            owners.append(owners_item)

        status = self.status.value

        business_area = self.business_area.to_dict()

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        about: Union[None, Unset, str]
        if isinstance(self.about, Unset):
            about = UNSET
        else:
            about = self.about

        lifecycle_id: Union[None, Unset, str]
        if isinstance(self.lifecycle_id, Unset):
            lifecycle_id = UNSET
        elif isinstance(self.lifecycle_id, UUID):
            lifecycle_id = str(self.lifecycle_id)
        else:
            lifecycle_id = self.lifecycle_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "external_id": external_id,
                "description": description,
                "access_type": access_type,
                "id": id,
                "owners": owners,
                "status": status,
                "business_area": business_area,
                "tags": tags,
            }
        )
        if about is not UNSET:
            field_dict["about"] = about
        if lifecycle_id is not UNSET:
            field_dict["lifecycle_id"] = lifecycle_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.business_area import BusinessArea
        from ..models.tag import Tag
        from ..models.user import User

        d = src_dict.copy()
        name = d.pop("name")

        external_id = d.pop("external_id")

        description = d.pop("description")

        access_type = DatasetAccessType(d.pop("access_type"))

        id = UUID(d.pop("id"))

        owners = []
        _owners = d.pop("owners")
        for owners_item_data in _owners:
            owners_item = User.from_dict(owners_item_data)

            owners.append(owners_item)

        status = DatasetStatus(d.pop("status"))

        business_area = BusinessArea.from_dict(d.pop("business_area"))

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        def _parse_about(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        about = _parse_about(d.pop("about", UNSET))

        def _parse_lifecycle_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                lifecycle_id_type_0 = UUID(data)

                return lifecycle_id_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        lifecycle_id = _parse_lifecycle_id(d.pop("lifecycle_id", UNSET))

        dataset = cls(
            name=name,
            external_id=external_id,
            description=description,
            access_type=access_type,
            id=id,
            owners=owners,
            status=status,
            business_area=business_area,
            tags=tags,
            about=about,
            lifecycle_id=lifecycle_id,
        )

        dataset.additional_properties = d
        return dataset

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
