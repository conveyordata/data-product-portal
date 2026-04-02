from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
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
    from ..models.postgre_sql_config import PostgreSQLConfig
    from ..models.redshift_config import RedshiftConfig
    from ..models.snowflake_config import SnowflakeConfig


T = TypeVar("T", bound="EnvironmentConfigsGetItem")


@_attrs_define
class EnvironmentConfigsGetItem:
    """
    Attributes:
        config (list[AWSGlueConfig | AWSS3Config | DatabricksConfig | PostgreSQLConfig | RedshiftConfig |
            SnowflakeConfig]):
        id (UUID):
        platform (Platform):
        environment (Environment):
        service (PlatformService):
    """

    config: list[
        AWSGlueConfig
        | AWSS3Config
        | DatabricksConfig
        | PostgreSQLConfig
        | RedshiftConfig
        | SnowflakeConfig
    ]
    id: UUID
    platform: Platform
    environment: Environment
    service: PlatformService
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.aws_glue_config import AWSGlueConfig
        from ..models.awss3_config import AWSS3Config
        from ..models.databricks_config import DatabricksConfig
        from ..models.redshift_config import RedshiftConfig
        from ..models.snowflake_config import SnowflakeConfig

        config = []
        for config_item_data in self.config:
            config_item: dict[str, Any]
            if isinstance(config_item_data, AWSS3Config):
                config_item = config_item_data.to_dict()
            elif isinstance(config_item_data, AWSGlueConfig):
                config_item = config_item_data.to_dict()
            elif isinstance(config_item_data, DatabricksConfig):
                config_item = config_item_data.to_dict()
            elif isinstance(config_item_data, SnowflakeConfig):
                config_item = config_item_data.to_dict()
            elif isinstance(config_item_data, RedshiftConfig):
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
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.aws_glue_config import AWSGlueConfig
        from ..models.awss3_config import AWSS3Config
        from ..models.databricks_config import DatabricksConfig
        from ..models.environment import Environment
        from ..models.platform import Platform
        from ..models.platform_service import PlatformService
        from ..models.postgre_sql_config import PostgreSQLConfig
        from ..models.redshift_config import RedshiftConfig
        from ..models.snowflake_config import SnowflakeConfig

        d = dict(src_dict)
        config = []
        _config = d.pop("config")
        for config_item_data in _config:

            def _parse_config_item(
                data: object,
            ) -> (
                AWSGlueConfig
                | AWSS3Config
                | DatabricksConfig
                | PostgreSQLConfig
                | RedshiftConfig
                | SnowflakeConfig
            ):
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    config_item_type_0 = AWSS3Config.from_dict(data)

                    return config_item_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    config_item_type_1 = AWSGlueConfig.from_dict(data)

                    return config_item_type_1
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    config_item_type_2 = DatabricksConfig.from_dict(data)

                    return config_item_type_2
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    config_item_type_3 = SnowflakeConfig.from_dict(data)

                    return config_item_type_3
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    config_item_type_4 = RedshiftConfig.from_dict(data)

                    return config_item_type_4
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                config_item_type_5 = PostgreSQLConfig.from_dict(data)

                return config_item_type_5

            config_item = _parse_config_item(config_item_data)

            config.append(config_item)

        id = UUID(d.pop("id"))

        platform = Platform.from_dict(d.pop("platform"))

        environment = Environment.from_dict(d.pop("environment"))

        service = PlatformService.from_dict(d.pop("service"))

        environment_configs_get_item = cls(
            config=config,
            id=id,
            platform=platform,
            environment=environment,
            service=service,
        )

        environment_configs_get_item.additional_properties = d
        return environment_configs_get_item

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
