import re
from typing import ClassVar, Self

from pydantic import model_validator
from sqlalchemy.orm import Session

from app.core.aws.get_url import get_aws_plugin_url
from app.technical_asset_configuration.base_schema import (
    PlatformMetadata,
    TechnicalAssetPlugin,
    UIElementMetadata,
    UIElementString,
)
from app.technical_asset_configuration.enums import UIElementType
from portal_plugins.parameter_store.model import (
    NAME,
)
from portal_plugins.parameter_store.model import (
    ParameterStoreTechnicalAssetConfiguration as ParameterStoreTechnicalAssetConfigurationModel,
)

VALID_LEVEL = re.compile(r"[A-Za-z0-9_.-]+")
MAX_LEVELS = 15
MAX_NAME_LENGTH = 1011
RESERVED_FOR_ARN_AND_ENVIRONMENT = 100


def _levels(path: str) -> list[str]:
    return [level for level in path.split("/") if level]


class ParameterStoreTechnicalAssetConfiguration(TechnicalAssetPlugin):
    name: ClassVar[str] = NAME
    version: ClassVar[str] = "1.0"

    prefix: str = ""
    parameter_name: str

    _platform_metadata = PlatformMetadata(
        result_string_template="/{prefix}/{parameter_name}",
        technical_info_template="/{environment}/{prefix}/{parameter_name}",
        display_name="Parameter Store",
        icon_name="parameter-store-logo.svg",
        icon_package="portal_plugins.parameter_store",
        platform_key="parameterstore",
        parent_platform="aws",
        result_label="Resulting parameter",
        result_tooltip="The parameter you can access through this technical asset",
        detailed_name="Parameter",
        shareable=False,
    )

    class Meta:
        orm_model = ParameterStoreTechnicalAssetConfigurationModel

    @model_validator(mode="after")
    def validate_parameter_name(self) -> Self:
        levels = _levels(self.prefix) + _levels(self.parameter_name)
        if not _levels(self.parameter_name):
            raise ValueError("The parameter name can't be empty")
        invalid = [level for level in levels if not VALID_LEVEL.fullmatch(level)]
        if invalid:
            raise ValueError(
                f"Parameter names can only contain letters, numbers, '_', '.', '-' and '/', not: {', '.join(invalid)}"
            )
        if len(levels) + 1 > MAX_LEVELS:
            raise ValueError(
                f"A parameter name can have at most {MAX_LEVELS} levels, including the environment"
            )
        if len("/".join(levels)) + RESERVED_FOR_ARN_AND_ENVIRONMENT > MAX_NAME_LENGTH:
            raise ValueError("The parameter name is too long")
        return self

    def render_template(self, template, **context):
        rendered = super().render_template(template, **context)
        return "/" + "/".join(part for part in rendered.split("/") if part)

    def get_configuration(self, configs: list) -> None:
        return None

    # Every AWS plugin shares the AWS tile on the data product page, so they all
    # use the same get_url. The portal refuses a parent tile whose children differ.
    get_url = classmethod(get_aws_plugin_url)

    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        base_metadata = super().get_ui_metadata(db)
        base_metadata += [
            UIElementMetadata(
                name="prefix",
                label="Prefix",
                required=True,
                type=UIElementType.String,
                string=UIElementString(initial_value=""),
                hidden=True,
                use_namespace_when_not_source_aligned=True,
            ),
            UIElementMetadata(
                name="parameter_name",
                label="Parameter name",
                type=UIElementType.String,
                tooltip="The name of the parameter to give access to. Use letters, numbers, '_', '.' and '-', and '/' to nest it deeper",
                required=True,
            ),
        ]
        return base_metadata
