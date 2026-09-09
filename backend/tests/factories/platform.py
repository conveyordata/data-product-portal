import factory
from faker import Faker

from app.configuration.platforms.model import Platform

fake = Faker()


class PlatformFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Platform

    id = factory.Faker("uuid4")
    name = factory.Sequence(lambda _: fake.unique.word())
