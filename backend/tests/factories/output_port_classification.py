import factory

from app.configuration.output_port_classifications.model import (
    OutputPortClassification,
)
from app.data_products.output_ports.enums import OutputPortAccessFunction


class OutputPortClassificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = OutputPortClassification
        # Without an explicit name this returns the seeded classification of access_function.
        sqlalchemy_get_or_create = ("name",)

    id = factory.Faker("uuid4")
    access_function = OutputPortAccessFunction.UNRESTRICTED
    name = factory.LazyAttribute(
        lambda o: OutputPortAccessFunction(o.access_function).name.title()
    )
    description = ""
