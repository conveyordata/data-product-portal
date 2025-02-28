import factory

from app.domains.model import Domain


class DomainFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Domain

    id = factory.Faker("uuid4")
    name = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=20)
