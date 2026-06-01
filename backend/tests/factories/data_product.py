import factory
from faker import Faker

from app.data_products.model import DataProduct
from app.data_products.status import DataProductStatus
from tests.factories.lifecycle import LifecycleFactory

from .data_product_type import DataProductTypeFactory
from .domain import DomainFactory

fake = Faker()


class DataProductFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProduct

    id = factory.Faker("uuid4")
    namespace = factory.LazyFunction(fake.unique.word)
    name = factory.LazyFunction(fake.unique.word)
    description = factory.Faker("text", max_nb_chars=20)
    about = factory.Faker("text", max_nb_chars=20)
    status = DataProductStatus.PENDING.value

    type = factory.SubFactory(DataProductTypeFactory)
    domain = factory.SubFactory(DomainFactory)
    lifecycle = factory.SubFactory(LifecycleFactory)
    usage = factory.Faker("word")
