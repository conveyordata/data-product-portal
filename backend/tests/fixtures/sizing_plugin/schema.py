from enum import Enum
from typing import Any, ClassVar
from uuid import UUID

from pydantic import model_validator
from sqlalchemy.orm import Session

from app.technical_asset_configuration.base_schema import (
    EnvironmentConfigurationError,
    EnvironmentFieldError,
    EnvironmentSettings,
    PlatformMetadata,
    PluginContext,
    SelectOption,
    TechnicalAssetPlugin,
    UIElementMetadata,
    env_field,
)
from app.technical_asset_configuration.enums import UIElementType
from tests.fixtures.sizing_plugin.model import NAME
from tests.fixtures.sizing_plugin.model import (
    SizingConfiguration as SizingConfigurationModel,
)
from tests.fixtures.sizing_plugin.model import (
    SizingTechnicalAssetConfiguration as SizingTechnicalAssetConfigurationModel,
)

FORBIDDEN_REPLICAS = 13
MODEL_LEVEL_FORBIDDEN_REPLICAS = 99


class Size(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"


class SizingConfigurationSchema(EnvironmentSettings):
    size: Size = env_field(
        label="Size",
        type=UIElementType.Select,
        options=[
            SelectOption(label="small", value=Size.small),
            SelectOption(label="medium", value=Size.medium),
            SelectOption(label="large", value=Size.large),
        ],
        default=Size.small,
        default_per_environment={
            "prd": Size.medium,
        },
        disabled_per_environment={
            "dev": {Size.large},
        },
    )
    replicas: int = env_field(
        label="Replicas",
        type=UIElementType.String,
        default=1,
        default_per_environment={
            "bad": "abc",
            "ulk": FORBIDDEN_REPLICAS,
        },
    )
    label: str = env_field(
        label="Label",
        type=UIElementType.String,
        default="{path}-{environment}",
        default_per_environment={
            "unk": "{missing}",
        },
    )

    @model_validator(mode="after")
    def _check_replicas(self):
        if self.replicas == MODEL_LEVEL_FORBIDDEN_REPLICAS:
            raise ValueError("Too many replicas")
        return self

    class Meta:
        orm_model = SizingConfigurationModel


class SizingTechnicalAssetConfiguration(TechnicalAssetPlugin):
    name: ClassVar[str] = NAME
    environment_configuration: ClassVar[type[EnvironmentSettings]] = (
        SizingConfigurationSchema
    )

    path: str

    _platform_metadata = PlatformMetadata(
        display_name="Sizing",
        icon_name="icon.svg",
        platform_key="sizing",
        detailed_name="Path",
    )

    class Meta:
        orm_model = SizingTechnicalAssetConfigurationModel

    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        return [
            UIElementMetadata(
                name="path", label="Path", type=UIElementType.String, required=True
            )
        ]

    def validate_environment_configuration(
        self,
        values: dict[UUID, dict[str, Any]],
        context: PluginContext,
        db: Session,
    ) -> None:
        errors = [
            EnvironmentFieldError(
                environment_id=environment_id,
                field="replicas",
                message="Unlucky number of replicas",
            )
            for environment_id, environment_values in values.items()
            if environment_values["replicas"] == FORBIDDEN_REPLICAS
        ]
        if errors:
            raise EnvironmentConfigurationError(errors)
