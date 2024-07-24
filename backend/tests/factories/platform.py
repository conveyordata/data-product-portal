import json

import factory
from factory.fuzzy import FuzzyChoice

from app.environments.enums import PlatformTypes
from app.environments.model import Platform

from . import EnvironmentFactory


class PlatformFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Platform

    id = factory.Faker("uuid4")
    name = FuzzyChoice(PlatformTypes)
    settings = json.dumps(
        {
            "account_id": "string",
            "kms_key": "string",
            "s3": {"bucket_arn": "string", "prefix_path": "string"},
            "glue": {"schema": "string", "table_prefixes": ["string"]},
        }
    )

    env = factory.SubFactory(EnvironmentFactory)
