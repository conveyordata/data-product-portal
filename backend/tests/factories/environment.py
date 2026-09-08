import factory
from faker import Faker

from app.configuration.environments.model import Environment

fake = Faker()


class EnvironmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Environment

    id = factory.Faker("uuid4")
    name = "dev"
    acronym = factory.Sequence(lambda _: fake.unique.word())
    context = "environment_context{{}}"
    is_default = False
