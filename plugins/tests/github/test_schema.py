from unittest.mock import Mock, patch
from uuid import uuid4

from portal_plugins.github.schema import GitHubPlugin


class TestGitHubPlugin:
    def test_get_platform_metadata__describes_the_github_tile(self):
        meta = GitHubPlugin.get_platform_metadata()
        assert meta.display_name == "GitHub"
        assert meta.platform_key == "github"
        assert meta.show_in_form is False
        assert meta.has_environments is False

    @patch("portal_plugins.github.schema.settings")
    def test_get_url__builds_repo_link_from_data_product_namespace(self, mock_settings):
        mock_settings.GITHUB_ORG = "UH-RDP"
        db = Mock()
        db.get.return_value = Mock(namespace="test-my-first-db")

        url = GitHubPlugin.get_url(uuid4(), db, actor=Mock())

        assert url == "https://github.com/UH-RDP/test-my-first-db"
