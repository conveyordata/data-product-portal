import uuid

from app.configuration.environments.model import Environment
from app.configuration.environments.platform_service_configurations.model import (
    EnvironmentPlatformServiceConfiguration,
)
from app.configuration.platforms.model import Platform
from app.configuration.platforms.platform_services.model import PlatformService
from app.data_output_configuration.azure_blob.schema import (
    AzureBlobTechnicalAssetConfiguration,
)
from app.data_output_configuration.base_schema import AssetProviderPlugin


def get_azure_blob_schema() -> AzureBlobTechnicalAssetConfiguration:
    data_output_configurations = AssetProviderPlugin.__subclasses__()
    for data_output_configuration in data_output_configurations:
        if (
            data_output_configuration.get_platform_metadata().platform_key
            == "azureblob"
        ):
            return data_output_configuration
    raise ValueError("Azure Blob schema not found")


class TestAzureBlobSchema:
    def test_get_platform_service_options(self, client, session):
        platform = Platform(id=uuid.uuid4(), name="azure")
        session.add(platform)
        platform_service = PlatformService(
            id=uuid.uuid4(),
            name="azureblob",
            result_string_template="",
            technical_info_template="",
            platform_id=platform.id,
            platform=platform,
        )
        session.add(platform_service)
        prod = Environment(id=uuid.uuid4(), name="production", acronym="prd")
        session.add(prod)
        env_service_config = EnvironmentPlatformServiceConfiguration(
            id=uuid.uuid4(),
            platform_id=platform.id,
            service_id=platform_service.id,
            environment_id=prod.id,
            config='[{"identifier": "prd", "storage_account_names": {"finance": "financeartifacts", "hr": "hrartifacts"}}]',
        )
        session.add(env_service_config)
        session.commit()
        schema = get_azure_blob_schema()
        domains = schema.get_platform_service_options_for_property(
            db=session, key="storage_account_names"
        )
        assert domains == {"finance", "hr"}
        identifiers = schema.get_platform_service_options_for_property(
            db=session, key="identifier"
        )
        assert identifiers == {"prd"}
