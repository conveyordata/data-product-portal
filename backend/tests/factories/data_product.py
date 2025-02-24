import factory

from app.data_products.model import DataProduct
from app.data_products.status import DataProductStatus

from .domain import DomainFactory
from .data_product_type import DataProductTypeFactory


class DataProductFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProduct

    id = factory.Faker("uuid4")
    name = factory.Faker("word")
    external_id = "external_id"
    description = factory.Faker("text", max_nb_chars=20)
    about = factory.Faker("text", max_nb_chars=20)
    status = DataProductStatus.PENDING.value

    type = factory.SubFactory(DataProductTypeFactory)
    domain = factory.SubFactory(DomainFactory)
