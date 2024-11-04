import factory
from tests.factories.schema import SchemaFactory

from app.data_contracts.schema.column.model import Column


class ColumnFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Column

    id = factory.Faker("uuid4")
    name = factory.Faker("word")
    description = factory.Faker("text")
    data_type = factory.Faker("word")
    checks = factory.Faker("word")

    schema = factory.SubFactory(SchemaFactory)
