import factory

from app.configuration.output_port_access_types.model import (
    OutputPortAccessType,
)
from app.data_products.output_ports.enums import OutputPortAccessFunction


class OutputPortAccessTypeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = OutputPortAccessType
        # This returns the default access type for access_function
        # (created per test in conftest) instead of inserting a duplicate.
        sqlalchemy_get_or_create = ("name",)

    id = factory.Faker("uuid4")
    access_function = OutputPortAccessFunction.UNRESTRICTED
    name = factory.LazyAttribute(
        lambda o: OutputPortAccessFunction(o.access_function).name.title()
    )
    description = ""
