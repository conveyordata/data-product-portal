import factory

from app.data_products.output_ports.table_schemas.model import OutputPortTableSchema

from .dataset import DatasetFactory


class OutputPortTableSchemaFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = OutputPortTableSchema

    id = factory.Faker("uuid4")
    output_port_id = factory.LazyAttribute(lambda o: DatasetFactory().id)
    name = factory.Faker("word")
    description = factory.Faker("sentence")
