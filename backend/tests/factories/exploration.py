import factory

from app.explorations.model import Exploration

from .domain import DomainFactory
from .user import UserFactory


class ExplorationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Exploration

    id = factory.Faker("uuid4")
    name = factory.Faker("word")
    namespace = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=20)
    domain = factory.SubFactory(DomainFactory)
    owner = factory.SubFactory(UserFactory)
