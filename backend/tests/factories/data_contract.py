import factory

from app.data_contracts.model import DataContract


class DataContractFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataContract

    id = factory.Faker("uuid4")
    table = factory.Faker("word")
    description = factory.Faker("text")
    checks = factory.Faker("word")
