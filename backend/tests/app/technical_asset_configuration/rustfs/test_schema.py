from unittest.mock import patch

from app.technical_asset_configuration.rustfs.schema import (
    RustFSTechnicalAssetConfiguration,
)
from tests.factories import DataProductFactory, UserFactory
from tests.session_util import as_user


class TestRustFSPlugin:
    def test_metadata(self):
        meta = RustFSTechnicalAssetConfiguration.get_platform_metadata()
        assert meta.display_name == "RustFS"
        assert meta.platform_key == "rustfs"
        assert meta.parent_platform is None
        assert meta.has_environments is False

    @patch("app.technical_asset_configuration.rustfs.schema.settings")
    def test_get_url_points_at_the_data_product_bucket(self, mock_settings, session):
        mock_settings.RUSTFS_CONSOLE_URL = "https://rustfs.example.com"
        mock_settings.RUSTFS_BUCKET_PREFIX = "dp-"
        data_product = DataProductFactory(namespace="test-my-first-db")

        user = UserFactory()
        with as_user(session, user.id):
            url = RustFSTechnicalAssetConfiguration.get_url(
                data_product.id, session, actor=user
            )

        assert url == (
            "https://rustfs.example.com/rustfs/console/browser/?bucket=dp-test-my-first-db"
        )
