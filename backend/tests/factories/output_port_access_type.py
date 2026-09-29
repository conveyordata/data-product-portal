import factory

from app.configuration.output_port_access_types.model import (
    OutputPortAccessType,
)
from app.data_products.output_ports.enums import OutputPortAccessFunction


class OutputPortAccessTypeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = OutputPortAccessType
        # Without an explicit name this returns the seeded access type of access_function.
        sqlalchemy_get_or_create = ("name",)

    id = factory.Faker("uuid4")
    access_function = OutputPortAccessFunction.UNRESTRICTED
    name = factory.LazyAttribute(
        lambda o: OutputPortAccessFunction(o.access_function).name.title()
    )
    description = ""
