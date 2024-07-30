import factory

from app.platforms.models import PlatformService

from .platform import PlatformFactory


class PlatformServiceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = PlatformService

    id = factory.Faker("uuid4")
    name = "S3"

    platform = factory.SubFactory(PlatformFactory)
