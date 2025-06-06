import factory

from app.platform_services.model import PlatformService

from .platform import PlatformFactory


class PlatformServiceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = PlatformService

    id = factory.Faker("uuid4")
    name = factory.Faker("word")
    result_string_template = factory.Faker("word")
    technical_info_template = factory.Faker("word")

    platform = factory.SubFactory(PlatformFactory)
