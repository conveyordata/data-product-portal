import factory

from app.platforms.models import PlatformServiceConfig

from .platform import PlatformFactory
from .platform_service import PlatformServiceFactory


class PlatformServiceConfigFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = PlatformServiceConfig

    id = factory.Faker("uuid4")
    config = '["identifier_1"]'

    platform = factory.SubFactory(PlatformFactory)
    service = factory.SubFactory(PlatformServiceFactory)
