import factory
from tests.factories.data_contract import DataContractFactory

from app.data_contracts.service_level_objective.model import ServiceLevelObjective


class ServiceLevelObjectiveFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ServiceLevelObjective

    id = factory.Faker("uuid4")
    type = factory.Faker("word")
    value = factory.Faker("word")
    severity = factory.Faker("word")

    data_contract = factory.SubFactory(DataContractFactory)
