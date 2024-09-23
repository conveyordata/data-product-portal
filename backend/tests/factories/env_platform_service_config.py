import json

import factory

from app.environment_platform_service_configurations.model import (
    EnvironmentPlatformServiceConfiguration,
)

from .environment import EnvironmentFactory
from .platform import PlatformFactory
from .platform_service import PlatformServiceFactory


class EnvPlatformServiceConfigFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = EnvironmentPlatformServiceConfiguration

    id = factory.Faker("uuid4")
    config = json.dumps(
        [
            {
                "identifier": "identifier",
                "bucket_name": "name1",
                "arn": "arn1",
                "kms_key": "kms1",
                "is_default": True,
            }
        ]
    )

    platform = factory.SubFactory(PlatformFactory)
    service = factory.SubFactory(PlatformServiceFactory)
    environment = factory.SubFactory(EnvironmentFactory)
