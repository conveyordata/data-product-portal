from typing import ClassVar, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.aws.get_url import get_aws_url
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
from app.users.schema import User


class ParameterStoreTechnicalAssetConfiguration(TechnicalAssetPlugin):
    name: ClassVar[str] = NAME
    version: ClassVar[str] = "1.0"

    prefix: str = ""
    parameter_name: str

    _platform_metadata = PlatformMetadata(
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

    def render_template(self, template, **context):
        rendered = super().render_template(template, **context)
        return "/" + "/".join(part for part in rendered.split("/") if part)

    def get_configuration(self, configs: list) -> None:
        return None

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        if environment is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Environment is required to get the URL for Parameter Store technical asset configurations",
            )
        return get_aws_url(id, db, actor, environment)

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
                tooltip="The name of the parameter to give access to",
                required=True,
            ),
        ]
        return base_metadata
