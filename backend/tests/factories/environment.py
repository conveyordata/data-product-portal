import factory

from app.environments.model import Environment


class EnvironmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Environment

    name = "dev"
    context = "environment_context{{}}"
    is_default = False
