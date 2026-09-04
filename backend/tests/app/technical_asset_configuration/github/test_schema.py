from unittest.mock import patch

from app.technical_asset_configuration.github.schema import GitHubPlugin
from tests.factories import DataProductFactory, UserFactory
from tests.session_util import as_user


class TestGitHubPlugin:
    def test_metadata(self):
        meta = GitHubPlugin.get_platform_metadata()
        assert meta.display_name == "GitHub"
        assert meta.platform_key == "github"
        assert meta.show_in_form is False
        assert meta.has_environments is False

    @patch("app.technical_asset_configuration.github.schema.settings")
    def test_get_url_builds_repo_link_from_data_product_namespace(
        self, mock_settings, session
    ):
        mock_settings.GITHUB_ORG = "UH-RDP"
        data_product = DataProductFactory(namespace="test-my-first-db")
        user = UserFactory()
        with as_user(session, user.id):
            url = GitHubPlugin.get_url(data_product.id, session, actor=user)

        assert url == "https://github.com/UH-RDP/test-my-first-db"
