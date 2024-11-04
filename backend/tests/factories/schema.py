import factory

from app.data_contracts.schema.model import Schema


class SchemaFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Schema

    id = factory.Faker("uuid4")
    table = factory.Faker("word")
    description = factory.Faker("text")
    checks = factory.Faker("word")
