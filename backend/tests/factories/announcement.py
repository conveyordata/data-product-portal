import factory

from app.data_products.output_ports.announcements.enums import AnnouncementType
from app.data_products.output_ports.announcements.model import Announcement
from tests.factories.output_port import OutputPortFactory


class AnnouncementFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Announcement

    id = factory.Faker("uuid4")
    output_port_id = factory.LazyFunction(lambda: OutputPortFactory().id)
    type = AnnouncementType.INFO
    title = factory.Faker("sentence", nb_words=6)
    message = factory.Faker("paragraph")
