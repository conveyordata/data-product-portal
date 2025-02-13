from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.platform import Platform


T = TypeVar("T", bound="PlatformService")


@_attrs_define
class PlatformService:
    """
    Attributes:
        id (UUID):
        name (str):
        platform (Platform):
    """

    id: UUID
    name: str
    platform: "Platform"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        platform = self.platform.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "platform": platform,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.platform import Platform

        d = src_dict.copy()
        id = UUID(d.pop("id"))

        name = d.pop("name")

        platform = Platform.from_dict(d.pop("platform"))

        platform_service = cls(
            id=id,
            name=name,
            platform=platform,
        )

        platform_service.additional_properties = d
        return platform_service

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
