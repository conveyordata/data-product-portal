import factory

from app.configuration.data_product_settings.model import DataProductSettingValue

from .data_product import DataProductFactory
from .data_product_setting import DataProductSettingFactory


class DataProductSettingValueFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductSettingValue

    id = factory.Faker("uuid4")
    value = factory.Faker("word")

    data_product_setting = factory.SubFactory(DataProductSettingFactory)
    data_product = factory.SubFactory(DataProductFactory)
