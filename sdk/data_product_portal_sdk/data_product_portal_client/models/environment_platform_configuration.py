from typing import TYPE_CHECKING, Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.aws_environment_platform_configuration import (
        AWSEnvironmentPlatformConfiguration,
    )
    from ..models.databricks_environment_platform_configuration import (
        DatabricksEnvironmentPlatformConfiguration,
    )
    from ..models.environment import Environment
    from ..models.platform import Platform


T = TypeVar("T", bound="EnvironmentPlatformConfiguration")


@_attrs_define
class EnvironmentPlatformConfiguration:
    """
    Attributes:
        config (Union['AWSEnvironmentPlatformConfiguration', 'DatabricksEnvironmentPlatformConfiguration']):
        id (UUID):
        environment (Environment):
        platform (Platform):
    """

    config: Union[
        "AWSEnvironmentPlatformConfiguration",
        "DatabricksEnvironmentPlatformConfiguration",
    ]
    id: UUID
    environment: "Environment"
    platform: "Platform"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.aws_environment_platform_configuration import (
            AWSEnvironmentPlatformConfiguration,
        )

        config: dict[str, Any]
        if isinstance(self.config, AWSEnvironmentPlatformConfiguration):
            config = self.config.to_dict()
        else:
            config = self.config.to_dict()

        id = str(self.id)

        environment = self.environment.to_dict()

        platform = self.platform.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config": config,
                "id": id,
                "environment": environment,
                "platform": platform,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.aws_environment_platform_configuration import (
            AWSEnvironmentPlatformConfiguration,
        )
        from ..models.databricks_environment_platform_configuration import (
            DatabricksEnvironmentPlatformConfiguration,
        )
        from ..models.environment import Environment
        from ..models.platform import Platform

        d = src_dict.copy()

        def _parse_config(
            data: object,
        ) -> Union[
            "AWSEnvironmentPlatformConfiguration",
            "DatabricksEnvironmentPlatformConfiguration",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                config_type_0 = AWSEnvironmentPlatformConfiguration.from_dict(data)

                return config_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            config_type_1 = DatabricksEnvironmentPlatformConfiguration.from_dict(data)

            return config_type_1

        config = _parse_config(d.pop("config"))

        id = UUID(d.pop("id"))

        environment = Environment.from_dict(d.pop("environment"))

        platform = Platform.from_dict(d.pop("platform"))

        environment_platform_configuration = cls(
            config=config,
            id=id,
            environment=environment,
            platform=platform,
        )

        environment_platform_configuration.additional_properties = d
        return environment_platform_configuration

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
