import factory

from app.environments.model import Environment


class EnvironmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Environment

    name = "dev"
    is_default = False
