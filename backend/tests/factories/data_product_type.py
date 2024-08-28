import factory

from app.data_product_types.enums import DataProductIconKey
from app.data_product_types.model import DataProductType


class DataProductTypeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductType

    id = factory.Faker("uuid4")
    name = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=20)
    icon_key = DataProductIconKey.DEFAULT.value
