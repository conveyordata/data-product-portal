import factory

from app.platforms.model import Platform


class PlatformFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Platform

    id = factory.Faker("uuid4")
    name = factory.Faker("word")
