import factory
from faker import Faker

from app.abstract_data_product.type import AbstractDataProductType
from app.access_durations.enums import AccessDurationType
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.model import Dataset
from app.data_products.output_ports.status import OutputPortStatus
from tests import test_session

from .access_duration import AccessDurationFactory
from .data_product import DataProductFactory
from .tags import TagFactory

fake = Faker()


class OutputPortFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Dataset

    id = factory.Faker("uuid4")
    namespace = factory.Sequence(lambda _: fake.unique.word())
    name = factory.Sequence(lambda _: fake.unique.word())
    description = factory.Faker("text", max_nb_chars=20)
    about = factory.Faker("text", max_nb_chars=20)
    status = OutputPortStatus.ACTIVE.value
    access_type = OutputPortAccessType.UNRESTRICTED.value
    usage = factory.Faker("word")
    data_product = factory.SubFactory(DataProductFactory)
    data_product_access_duration_type = AccessDurationType.PERMANENT.value
    exploration_access_duration_type = AccessDurationType.PERMANENT.value

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

    @factory.post_generation
    def access_durations(self, create, extracted, **kwargs):
        if not create:
            return

        for abstract_type, duration_type in (
            (
                AbstractDataProductType.DATA_PRODUCT,
                self.data_product_access_duration_type,
            ),
            (
                AbstractDataProductType.EXPLORATION,
                self.exploration_access_duration_type,
            ),
        ):
            if duration_type == AccessDurationType.PERMANENT:
                AccessDurationFactory(
                    abstract_data_product_type=abstract_type,
                    access_duration_type=AccessDurationType.PERMANENT,
                    days=None,
                )
        test_session.commit()
