import factory

from app.configuration.output_port_classifications.model import (
    OutputPortClassification,
)
from app.data_products.output_ports.enums import OutputPortAccessType


class OutputPortClassificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = OutputPortClassification
        # Without an explicit name this returns the seeded classification of access_type.
        sqlalchemy_get_or_create = ("name",)

    id = factory.Faker("uuid4")
    access_type = OutputPortAccessType.UNRESTRICTED
    name = factory.LazyAttribute(
        lambda o: OutputPortAccessType(o.access_type).name.title()
    )
    description = ""
