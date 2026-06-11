import factory
from faker import Faker

from app.explorations.model import Exploration

from .domain import DomainFactory
from .user import UserFactory

fake = Faker()


class ExplorationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Exploration

    id = factory.Faker("uuid4")
    name = factory.LazyFunction(fake.unique.word)
    namespace = factory.LazyFunction(fake.unique.word)
    description = factory.Faker("text", max_nb_chars=20)
    domain = factory.SubFactory(DomainFactory)
    owner = factory.SubFactory(UserFactory)
