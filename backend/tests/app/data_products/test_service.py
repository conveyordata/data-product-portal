from app.data_products.model import DataProduct
from app.data_products.service import DataProductService
from app.data_products.technical_assets.model import TechnicalAsset
from app.technical_asset_configuration.base_model import TechnicalAssetConfiguration
from tests.factories import DataProductFactory, TechnicalAssetFactory


class TestDataProductService:
    def test_remove_data_product__deletes_technical_assets_and_configurations(
        self, session
    ):
        data_product = DataProductFactory()
        technical_asset = TechnicalAssetFactory(owner=data_product)
        data_product_id = data_product.id
        technical_asset_id = technical_asset.id
        configuration_id = technical_asset.configuration_id
        configuration_type = type(technical_asset.configuration)

        DataProductService(session).remove_data_product(data_product_id)

        assert session.get(DataProduct, data_product_id) is None
        assert session.get(TechnicalAsset, technical_asset_id) is None
        assert session.get(configuration_type, configuration_id) is None
        assert session.get(TechnicalAssetConfiguration, configuration_id) is None
