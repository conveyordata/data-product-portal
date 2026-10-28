import factory

from app.data_products.technical_assets.model import TechnicalAssetAccessMode
from tests.factories.access_mode import AccessModeFactory
from tests.factories.technical_asset import TechnicalAssetFactory


class TechnicalAssetAccessModeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TechnicalAssetAccessMode
        exclude = (
            "technical_asset",
            "access_mode",
        )

    technical_asset = factory.SubFactory(TechnicalAssetFactory)
    technical_asset_id = factory.SelfAttribute("technical_asset.id")
    access_mode = factory.SubFactory(AccessModeFactory)
    access_mode_id = factory.SelfAttribute("access_mode.id")
