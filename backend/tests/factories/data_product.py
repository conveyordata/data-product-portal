import factory
from faker import Faker

from app.data_products.model import DataProduct
from app.data_products.status import AbstractDataProductStatus
from tests.factories.lifecycle import LifecycleFactory

from .data_product_type import DataProductTypeFactory
from .domain import DomainFactory

fake = Faker()


class DataProductFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProduct

    id = factory.Faker("uuid4")
    namespace = factory.Sequence(lambda _: fake.unique.word())
    name = factory.Sequence(lambda _: fake.unique.word())
    description = factory.Faker("text", max_nb_chars=20)
    about = factory.Faker("text", max_nb_chars=20)
    status = AbstractDataProductStatus.PENDING.value

    type = factory.SubFactory(DataProductTypeFactory)
    domain = factory.SubFactory(DomainFactory)
    lifecycle = factory.SubFactory(LifecycleFactory)
    usage = factory.Faker("word")
