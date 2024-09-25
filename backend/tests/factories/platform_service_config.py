import factory

from app.platform_service_configurations.model import PlatformServiceConfiguration

from .platform import PlatformFactory
from .platform_service import PlatformServiceFactory


class PlatformServiceConfigFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = PlatformServiceConfiguration

    id = factory.Faker("uuid4")
    config = '["identifier_1"]'

    platform = factory.SubFactory(PlatformFactory)
    service = factory.SubFactory(PlatformServiceFactory)
