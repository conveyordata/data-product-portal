import json
from typing import ClassVar, Literal, Optional, Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.configuration.environments.platform_service_configurations.model import (
    EnvironmentPlatformServiceConfiguration,
)
from app.configuration.environments.platform_service_configurations.schema_response import (
    EnvironmentConfigsGetItem,
)
from app.configuration.platforms.platform_services.model import (
    PlatformService as PlatformServiceModel,
)
from app.data_output_configuration.azure_blob.model import (
    AzureBlobTechnicalAssetConfiguration as AzureBlobTechnicalAssetConfigurationModel,
)
from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    PlatformMetadata,
    SelectOption,
    UIElementMetadata,
    UIElementSelect,
    UIElementString,
)
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.enums import UIElementType
from app.data_products.schema import DataProduct
from app.users.schema import User


class AzureBlobTechnicalAssetConfiguration(AssetProviderPlugin):
    name: ClassVar[str] = "AzureBlobTechnicalAssetConfiguration"
    version: ClassVar[str] = "1.0"

    storage_account: str
    path: str = ""
    container_name: str

    configuration_type: Literal[DataOutputTypes.AzureBlobTechnicalAssetConfiguration]

    _platform_metadata = PlatformMetadata(
        display_name="Blob",
        icon_name="azure-storage-account-logo.svg",
        platform_key="azureblob",
        parent_platform="azure",
        result_label="Resulting path",
        result_tooltip="The path you can access through this technical asset",
        detailed_name="Path",
    )

    class Meta:
        orm_model = AzureBlobTechnicalAssetConfigurationModel

    def validate_configuration(self, data_product: DataProduct):
        pass

    def on_create(self):
        pass

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        return "https://portal.azure.com/"

    @classmethod
    def extract_entries_from_config(
        cls, configs: Sequence[EnvironmentConfigsGetItem], key: str
    ):
        if not configs:
            raise NotImplementedError("No platform service configuration found")
        options: set[str] = set()
        for env_config in configs:
            if not isinstance(env_config.config, str):
                continue
            service_configs = json.loads(env_config.config)
            for config_item in service_configs:
                value = config_item.get(key)
                if value is None:
                    continue

                if isinstance(value, dict):
                    options.update(value.keys())
                else:
                    options.add(str(value))

        return options

    @classmethod
    def get_platform_service_options_for_property(
        cls, db: Session, key: str
    ) -> set[str]:
        """Get a specific enviornment platform configuration from the database if needed"""
        if not cls._platform_metadata:
            raise NotImplementedError("Platform metadata not defined for this plugin")

        service = db.scalar(
            select(PlatformServiceModel).where(
                func.lower(PlatformServiceModel.name)
                == cls._platform_metadata.platform_key
            )
        )
        if not service:
            raise NotImplementedError("No platform service found")
        configs: Sequence[EnvironmentConfigsGetItem] = db.scalars(
            select(EnvironmentPlatformServiceConfiguration).where(
                EnvironmentPlatformServiceConfiguration.service_id == service.id
            )
        ).all()
        return cls.extract_entries_from_config(configs, key)

    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        base_metadata = super().get_ui_metadata(db)
        domains = cls.get_platform_service_options_for_property(
            db, "storage_account_names"
        )
        base_metadata += [
            UIElementMetadata(
                name="storage_account",
                label="Storage Account of domain",
                type=UIElementType.Select,
                required=True,
                tooltip="The storage account of your domain.",
                select=UIElementSelect(
                    options=[
                        SelectOption(value=domain, label=domain) for domain in domains
                    ]
                ),
            ),
            UIElementMetadata(
                name="container_name",
                label="Container",
                required=True,
                type=UIElementType.String,
                string=UIElementString(initial_value=""),
            ),
            UIElementMetadata(
                name="path",
                label="Path",
                required=False,
                type=UIElementType.String,
                tooltip="The name of the path to give write access to",
                string=UIElementString(initial_value=""),
            ),
        ]
        return base_metadata
