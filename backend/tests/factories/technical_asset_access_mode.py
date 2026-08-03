import factory

from app.data_products.technical_assets.model import TechnicalAssetAccessMode
from tests.factories.technical_asset import TechnicalAssetFactory


class TechnicalAssetAccessModeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TechnicalAssetAccessMode
        exclude = ("technical_asset",)

    technical_asset = factory.SubFactory(TechnicalAssetFactory)
    technical_asset_id = factory.SelfAttribute("technical_asset.id")
    name = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=120)
