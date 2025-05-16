import factory

from app.platform_services.model import PlatformService

from .platform import PlatformFactory


class PlatformServiceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = PlatformService

    id = factory.Faker("uuid4")
    name = factory.Faker("word")
    template = factory.Faker("word")

    platform = factory.SubFactory(PlatformFactory)
