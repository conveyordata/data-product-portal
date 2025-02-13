from typing import TYPE_CHECKING, Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.aws_glue_config import AWSGlueConfig
    from ..models.awss3_config import AWSS3Config
    from ..models.databricks_config import DatabricksConfig
    from ..models.environment import Environment
    from ..models.platform import Platform
    from ..models.platform_service import PlatformService


T = TypeVar("T", bound="EnvironmentPlatformServiceConfiguration")


@_attrs_define
class EnvironmentPlatformServiceConfiguration:
    """
    Attributes:
        config (list[Union['AWSGlueConfig', 'AWSS3Config', 'DatabricksConfig']]):
        id (UUID):
        platform (Platform):
        environment (Environment):
        service (PlatformService):
    """

    config: list[Union["AWSGlueConfig", "AWSS3Config", "DatabricksConfig"]]
    id: UUID
    platform: "Platform"
    environment: "Environment"
    service: "PlatformService"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.aws_glue_config import AWSGlueConfig
        from ..models.awss3_config import AWSS3Config

        config = []
        for config_item_data in self.config:
            config_item: dict[str, Any]
            if isinstance(config_item_data, AWSS3Config):
                config_item = config_item_data.to_dict()
            elif isinstance(config_item_data, AWSGlueConfig):
                config_item = config_item_data.to_dict()
            else:
                config_item = config_item_data.to_dict()

            config.append(config_item)

        id = str(self.id)

        platform = self.platform.to_dict()

        environment = self.environment.to_dict()

        service = self.service.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config": config,
                "id": id,
                "platform": platform,
                "environment": environment,
                "service": service,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.aws_glue_config import AWSGlueConfig
        from ..models.awss3_config import AWSS3Config
        from ..models.databricks_config import DatabricksConfig
        from ..models.environment import Environment
        from ..models.platform import Platform
        from ..models.platform_service import PlatformService

        d = src_dict.copy()
        config = []
        _config = d.pop("config")
        for config_item_data in _config:

            def _parse_config_item(
                data: object,
            ) -> Union["AWSGlueConfig", "AWSS3Config", "DatabricksConfig"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    config_item_type_0 = AWSS3Config.from_dict(data)

                    return config_item_type_0
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    config_item_type_1 = AWSGlueConfig.from_dict(data)

                    return config_item_type_1
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                config_item_type_2 = DatabricksConfig.from_dict(data)

                return config_item_type_2

            config_item = _parse_config_item(config_item_data)

            config.append(config_item)

        id = UUID(d.pop("id"))

        platform = Platform.from_dict(d.pop("platform"))

        environment = Environment.from_dict(d.pop("environment"))

        service = PlatformService.from_dict(d.pop("service"))

        environment_platform_service_configuration = cls(
            config=config,
            id=id,
            platform=platform,
            environment=environment,
            service=service,
        )

        environment_platform_service_configuration.additional_properties = d
        return environment_platform_service_configuration

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
