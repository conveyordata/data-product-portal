import factory

from tests.fixtures.fake_plugin.model import FakeTechnicalAssetConfiguration
from tests.fixtures.sizing_plugin.model import (
    SizingConfiguration,
    SizingTechnicalAssetConfiguration,
)


class TechnicalAssetConfigurationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = FakeTechnicalAssetConfiguration

    id = factory.Faker("uuid4")
    path = "path"
    granular = False
    table = ""


class SizingTechnicalAssetConfigurationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SizingTechnicalAssetConfiguration

    id = factory.Faker("uuid4")
    path = "path"


class SizingConfigurationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SizingConfiguration
