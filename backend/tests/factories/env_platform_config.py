import json

import factory

from app.environments.model import EnvPlatformConfig

from .environment import EnvironmentFactory
from .platform import PlatformFactory


class EnvPlatformConfigFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = EnvPlatformConfig

    id = factory.Faker("uuid4")
    config = json.dumps(
        {"account_id": "111", "region": "us", "can_read_from": ["test"]}
    )

    platform = factory.SubFactory(PlatformFactory)
    environment = factory.SubFactory(EnvironmentFactory)
