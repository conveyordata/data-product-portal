from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_product_status import DataProductStatus

if TYPE_CHECKING:
    from ..models.data_product_type_create import DataProductTypeCreate


T = TypeVar("T", bound="BaseDataProductGet")


@_attrs_define
class BaseDataProductGet:
    """
    Attributes:
        id (UUID):
        name (str):
        description (str):
        about (Union[None, str]):
        external_id (str):
        status (DataProductStatus):
        type_ (DataProductTypeCreate):
    """

    id: UUID
    name: str
    description: str
    about: Union[None, str]
    external_id: str
    status: DataProductStatus
    type_: "DataProductTypeCreate"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        description = self.description

        about: Union[None, str]
        about = self.about

        external_id = self.external_id

        status = self.status.value

        type_ = self.type_.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "about": about,
                "external_id": external_id,
                "status": status,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.data_product_type_create import DataProductTypeCreate

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

        status = DataProductStatus(d.pop("status"))

        type_ = DataProductTypeCreate.from_dict(d.pop("type"))

        base_data_product_get = cls(
            id=id,
            name=name,
            description=description,
            about=about,
            external_id=external_id,
            status=status,
            type_=type_,
        )

        base_data_product_get.additional_properties = d
        return base_data_product_get

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
