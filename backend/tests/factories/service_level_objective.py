import factory
from tests.factories.schema import SchemaFactory

from app.data_contracts.service_level_objective.model import ServiceLevelObjective


class ServiceLevelObjectiveFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ServiceLevelObjective

    id = factory.Faker("uuid4")
    type = factory.Faker("word")
    value = factory.Faker("word")
    severity = factory.Faker("word")

    schema = factory.SubFactory(SchemaFactory)
