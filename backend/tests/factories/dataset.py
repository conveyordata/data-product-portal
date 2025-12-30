import factory

from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.model import Dataset
from app.data_products.output_ports.status import OutputPortStatus
from tests import test_session

from .data_product import DataProductFactory
from .tags import TagFactory


class DatasetFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Dataset

    id = factory.Faker("uuid4")
    namespace = factory.Faker("word")
    name = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=20)
    about = factory.Faker("text", max_nb_chars=20)
    status = OutputPortStatus.ACTIVE.value
    access_type = OutputPortAccessType.PUBLIC.value
    usage = factory.Faker("word")
    data_product = factory.SubFactory(DataProductFactory)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            # If we are just doing DataOutputFactory.build(), don't save tags
            return

        if extracted:
            # If called as: DataOutputFactory(tags=[tag1, tag2])
            for tag in extracted:
                self.tags.append(tag)
        else:
            # If called without arguments, create a default tag
            self.tags.append(TagFactory())
        test_session.commit()
