import factory

from app.configuration.platform_service_configurations.model import (
    PlatformServiceConfiguration,
)

from .platform_service import PlatformServiceFactory


class PlatformServiceConfigFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = PlatformServiceConfiguration

    id = factory.Faker("uuid4")
    config = '["identifier_1"]'

    service = factory.SubFactory(PlatformServiceFactory)
    platform = factory.SelfAttribute("service.platform")
