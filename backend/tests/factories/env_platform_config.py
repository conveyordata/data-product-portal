import json

import factory

from app.environment_platform_configurations.model import (
    EnvironmentPlatformConfiguration,
)

from .environment import EnvironmentFactory
from .platform import PlatformFactory


class EnvPlatformConfigFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = EnvironmentPlatformConfiguration

    id = factory.Faker("uuid4")
    config = json.dumps(
        {"account_id": "111", "region": "us", "can_read_from": ["test"]}
    )

    platform = factory.SubFactory(PlatformFactory)
    environment = factory.SubFactory(EnvironmentFactory)
