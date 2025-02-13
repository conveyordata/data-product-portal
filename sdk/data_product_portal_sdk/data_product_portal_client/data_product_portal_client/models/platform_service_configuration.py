from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.platform import Platform
    from ..models.platform_service import PlatformService


T = TypeVar("T", bound="PlatformServiceConfiguration")


@_attrs_define
class PlatformServiceConfiguration:
    """
    Attributes:
        id (UUID):
        platform (Platform):
        service (PlatformService):
        config (list[str]):
    """

    id: UUID
    platform: "Platform"
    service: "PlatformService"
    config: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        platform = self.platform.to_dict()

        service = self.service.to_dict()

        config = self.config

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "platform": platform,
                "service": service,
                "config": config,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.platform import Platform
        from ..models.platform_service import PlatformService

        d = src_dict.copy()
        id = UUID(d.pop("id"))

        platform = Platform.from_dict(d.pop("platform"))

        service = PlatformService.from_dict(d.pop("service"))

        config = cast(list[str], d.pop("config"))

        platform_service_configuration = cls(
            id=id,
            platform=platform,
            service=service,
            config=config,
        )

        platform_service_configuration.additional_properties = d
        return platform_service_configuration

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
