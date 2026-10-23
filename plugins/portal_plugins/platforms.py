from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.configuration.platforms.service import PlatformSettingsService
from app.core.aws.get_url import get_aws_url
from app.core.conveyor.notebook_builder import CONVEYOR_SERVICE
from app.data_products.model import DataProduct as DataProductModel
from app.plugins.platform import OverridableProperty, Platform, ToolType
from app.settings import settings
from app.users.schema import User
from portal_plugins.azure_blob.schema import AzureBlobTechnicalAssetConfiguration
from portal_plugins.databricks.schema import DatabricksTechnicalAssetConfiguration
from portal_plugins.glue.schema import GlueTechnicalAssetConfiguration
from portal_plugins.osi_sem_model.schema import (
    OSISemanticModelTechnicalAssetConfiguration,
)
from portal_plugins.parameter_store.schema import (
    ParameterStoreTechnicalAssetConfiguration,
)
from portal_plugins.postgresql.schema import PostgreSQLTechnicalAssetConfiguration
from portal_plugins.redshift.schema import RedshiftTechnicalAssetConfiguration
from portal_plugins.s3.schema import S3TechnicalAssetConfiguration
from portal_plugins.settings import (
    AWSSettings,
    AzureSettings,
    DatabricksSettings,
    PostgreSQLSettings,
    SnowflakeSettings,
)
from portal_plugins.snowflake.schema import SnowflakeTechnicalAssetConfiguration


class AWSPlatform(Platform):
    key = "aws"
    display_name = "AWS"
    icon_name = "aws-logo.svg"
    settings_model = AWSSettings
    asset_types = [
        S3TechnicalAssetConfiguration,
        GlueTechnicalAssetConfiguration,
        RedshiftTechnicalAssetConfiguration,
        ParameterStoreTechnicalAssetConfiguration,
    ]

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        if environment is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Environment is required to get the AWS URL",
            )
        return get_aws_url(id, db, actor, environment)


class AzurePlatform(Platform):
    key = "azure"
    display_name = "Azure"
    icon_name = "azure-logo.svg"
    settings_model = AzureSettings
    asset_types = [AzureBlobTechnicalAssetConfiguration]

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        return "https://portal.azure.com/"


class DatabricksPlatform(Platform):
    key = "databricks"
    display_name = "Databricks"
    icon_name = "databricks-logo.svg"
    icon_package = "portal_plugins.databricks"
    settings_model = DatabricksSettings
    asset_types = [DatabricksTechnicalAssetConfiguration]

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        workspace_urls = DatabricksSettings.model_validate(
            PlatformSettingsService(db).get_for_environment_name(cls.key, environment)
        ).workspace_urls
        data_product = db.get(DataProductModel, id)
        if str(data_product.domain_id) not in workspace_urls:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace not configured for domain {data_product.domain.name}",
            )
        return workspace_urls[str(data_product.domain_id)]


class SnowflakePlatform(Platform):
    key = "snowflake"
    display_name = "Snowflake"
    icon_name = "snowflake-logo.svg"
    icon_package = "portal_plugins.snowflake"
    settings_model = SnowflakeSettings
    asset_types = [SnowflakeTechnicalAssetConfiguration]

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        login_url = SnowflakeSettings.model_validate(
            PlatformSettingsService(db).get_for_environment_name(cls.key, environment)
        ).login_url
        if not login_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="login_url missing from Snowflake settings",
            )
        return login_url


class PostgreSQLPlatform(Platform):
    key = "postgresql"
    display_name = "PostgreSQL"
    icon_name = "postgresql-logo.svg"
    icon_package = "portal_plugins.postgresql"
    settings_model = PostgreSQLSettings
    asset_types = [PostgreSQLTechnicalAssetConfiguration]
    tool_types = [
        ToolType(
            name="PostgreSQLInstance",
            display_name="PostgreSQL instance",
            overridable_properties=[
                OverridableProperty(
                    name="engine_version",
                    label="Engine version",
                    allowed_values=["15", "16", "17"],
                    default="16",
                ),
                OverridableProperty(
                    name="size",
                    label="Size",
                    allowed_values=["small", "medium", "large"],
                    default="small",
                ),
                OverridableProperty(
                    name="storage_gb",
                    label="Storage (GB)",
                    allowed_values=["20", "50", "100"],
                    default="20",
                ),
            ],
        )
    ]

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        return ""


class OSIPlatform(Platform):
    key = "osi"
    display_name = "OSI"
    icon_name = "osi-logo.svg"
    icon_package = "portal_plugins.osi_sem_model"
    asset_types = [OSISemanticModelTechnicalAssetConfiguration]

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        return ""


class GitHubPlatform(Platform):
    key = "github"
    display_name = "GitHub"
    icon_name = "github-logo.svg"
    icon_package = "portal_plugins.github"
    has_environments = False
    tool_types = [ToolType(name="GitHubPlugin", display_name="GitHub repository")]

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        data_product = db.get(DataProductModel, id)
        return f"https://github.com/{settings.GITHUB_ORG}/{data_product.namespace}"


class ConveyorPlatform(Platform):
    key = "conveyor"
    display_name = "Conveyor"
    icon_name = "conveyor-logo.svg"
    icon_package = "portal_plugins.conveyor"
    has_environments = False
    tool_types = [ToolType(name="ConveyorPlugin", display_name="Conveyor project")]

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        data_product = db.get(DataProductModel, id)
        return CONVEYOR_SERVICE.generate_ide_url(data_product.namespace)


class AgnoPlatform(Platform):
    key = "agno"
    display_name = "Agno"
    icon_name = "agno-logo.svg"
    icon_package = "portal_plugins.agno"
    has_environments = False
    tool_types = [ToolType(name="AgnoPlugin", display_name="Agno agent")]

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        data_product = db.get(DataProductModel, id)
        return f"https://os.agno.com/chat?type=agent&id={data_product.namespace}-agent"
