import factory

from tests.fixtures.fake_plugin.model import FakeTechnicalAssetConfiguration


class TechnicalAssetConfigurationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = FakeTechnicalAssetConfiguration

    id = factory.Faker("uuid4")
    path = "path"
    granular = False
    table = ""
