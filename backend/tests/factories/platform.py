import factory

from app.platforms.models import Platform


class PlatformFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Platform

    id = factory.Faker("uuid4")
    name = "AWS"
