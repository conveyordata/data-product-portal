import factory

from app.configuration.domains.model import Domain


class DomainFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Domain

    id = factory.Faker("uuid4")
    name = factory.Faker("word")
    namespace = factory.Sequence(lambda n: f"domain-{n}")
    description = factory.Faker("text", max_nb_chars=20)
