import json

import factory

from app.environments.model import EnvPlatformServiceConfig

from .environment import EnvironmentFactory
from .platform import PlatformFactory
from .platform_service import PlatformServiceFactory


class EnvPlatformServiceConfigFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = EnvPlatformServiceConfig

    id = factory.Faker("uuid4")
    config = json.dumps(
        {
            "bucket_1": {
                "account_id": 10,
                "name": "name1",
                "arn": "arn1",
                "kms": "kms1",
            }
        }
    )

    platform = factory.SubFactory(PlatformFactory)
    service = factory.SubFactory(PlatformServiceFactory)
    environment = factory.SubFactory(EnvironmentFactory)
