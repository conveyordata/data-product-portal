import factory

from app.data_products.output_ports.table_schemas.model import OutputPortColumn

from .output_port_table_schema import OutputPortTableSchemaFactory


class OutputPortColumnFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = OutputPortColumn

    id = factory.Faker("uuid4")
    table_schema_id = factory.LazyAttribute(lambda o: OutputPortTableSchemaFactory().id)
    name = factory.Faker("word")
    description = factory.Faker("sentence")
    data_type = "varchar"
