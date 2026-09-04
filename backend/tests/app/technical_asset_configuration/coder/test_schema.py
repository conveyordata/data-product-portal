from unittest.mock import patch

from app.technical_asset_configuration.coder.schema import CoderPlugin
from tests.factories import DataProductFactory, UserFactory
from tests.session_util import as_user


class TestCoderPlugin:
    def test_metadata(self):
        meta = CoderPlugin.get_platform_metadata()
        assert meta.display_name == "Coder"
        assert meta.platform_key == "coder"
        assert meta.show_in_form is False
        assert meta.has_environments is False

    @patch("app.technical_asset_configuration.coder.schema.settings")
    def test_get_url_builds_workspace_link_from_data_product_namespace(
        self, mock_settings, session
    ):
        mock_settings.CODER_BASE_URL = "https://ide.example.com"
        mock_settings.CODER_GITHUB_ORG = "example-org"
        data_product = DataProductFactory(namespace="test-my-first-db")
        user = UserFactory()
        with as_user(session, user.id):
            url = CoderPlugin.get_url(data_product.id, session, actor=user)

        assert url == (
            "https://ide.example.com/templates/vscode/workspace"
            "?param.git_repo=https://github.com/example-org/test-my-first-db"
        )
