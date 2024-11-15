import factory
from tests.factories.data_contract import DataContractFactory

from app.data_contracts.column.model import Column


class ColumnFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Column

    id = factory.Faker("uuid4")
    name = factory.Faker("word")
    description = factory.Faker("text")
    data_type = factory.Faker("word")
    checks = factory.Faker("word")

    data_contract = factory.SubFactory(DataContractFactory)
