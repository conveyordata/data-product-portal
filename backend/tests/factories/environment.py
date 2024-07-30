import factory

from app.environments.model import Environment


class EnvironmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Environment

    id = factory.Faker("uuid4")
    name = "dev"
    context = "environment_context{{}}"
    is_default = False
