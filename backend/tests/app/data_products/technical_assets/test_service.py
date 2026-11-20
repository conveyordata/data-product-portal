from app.data_products.technical_assets.model import TechnicalAsset
from app.data_products.technical_assets.service import TechnicalAssetService
from app.technical_asset_configuration.base_model import TechnicalAssetConfiguration
from tests.factories import TechnicalAssetFactory


class TestTechnicalAssetService:
    def test_remove_technical_asset__deletes_configuration(self, session):
        technical_asset = TechnicalAssetFactory()
        technical_asset_id = technical_asset.id
        configuration_id = technical_asset.configuration_id
        configuration_type = type(technical_asset.configuration)

        TechnicalAssetService(session).remove_technical_asset(
            technical_asset.owner_id, technical_asset_id
        )

        assert session.get(TechnicalAsset, technical_asset_id) is None
        assert session.get(configuration_type, configuration_id) is None
        assert session.get(TechnicalAssetConfiguration, configuration_id) is None
