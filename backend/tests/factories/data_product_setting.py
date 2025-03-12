import factory

from app.data_product_settings.model import DataProductSetting


class DataProductSettingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductSetting

    id = factory.Faker("uuid4")
    external_id = "external_id"
    tooltip = factory.Faker("text", max_nb_chars=20)
    name = factory.Faker("word")
    type = "checkbox"
    category = factory.Faker("word")
    default = "True"
    order = factory.Faker("pyint")
    scope = "dataproduct"
