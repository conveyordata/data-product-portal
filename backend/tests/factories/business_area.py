import factory

from app.business_areas.model import BusinessArea


class BusinessAreaFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = BusinessArea

    id = factory.Faker("uuid4")
    name = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=20)
