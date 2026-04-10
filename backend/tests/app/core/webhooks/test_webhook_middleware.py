"""Tests for webhook middleware functionality."""

import uuid
from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from starlette.routing import _DefaultLifespan

from app.main import app
from app.settings import settings


@contextmanager
def webhook_config(webhook_url: str | None = "http://test-webhook.example.com/hook"):
    """Context manager to temporarily set webhook configuration."""
    original_webhook_url = settings.WEBHOOK_URL
    original_webhook_secret = settings.WEBHOOK_SECRET

    settings.WEBHOOK_URL = webhook_url
    settings.WEBHOOK_SECRET = "test-secret" if webhook_url else None

    try:
        yield
    finally:
        settings.WEBHOOK_URL = original_webhook_url
        settings.WEBHOOK_SECRET = original_webhook_secret


@contextmanager
def test_client_context():
    """Create a test client with disabled lifespan for testing."""
    # Disable lifespan for testing to avoid MCP server conflicts
    app.router.lifespan_context = _DefaultLifespan(app.router)

    with TestClient(app) as client:
        yield client


class TestWebhookMiddleware:
    """Test cases for webhook middleware."""

    @patch("app.main.call_webhook")
    def test_webhook_called_for_post_request(self, mock_call_webhook: MagicMock):
        """Test that webhook is called for POST requests to regular endpoints."""
        mock_call_webhook.return_value = AsyncMock()

        with webhook_config(), test_client_context() as client:
            # Make a POST request to a non-filtered endpoint
            client.post(
                "/api/data_products",
                json={"name": "test"},
            )

        # Verify webhook was called
        assert mock_call_webhook.called

    @patch("app.main.call_webhook")
    def test_webhook_called_for_put_request(self, mock_call_webhook: MagicMock):
        """Test that webhook is called for PUT requests to regular endpoints."""
        mock_call_webhook.return_value = AsyncMock()

        with webhook_config(), test_client_context() as client:
            # Make a PUT request to a non-filtered endpoint
            # Use a valid UUID to avoid validation errors
            test_uuid = str(uuid.uuid4())
            client.put(
                f"/api/data_products/{test_uuid}",
                json={"name": "updated"},
            )

        # Verify webhook was called
        assert mock_call_webhook.called

    @patch("app.main.call_webhook")
    def test_webhook_called_for_delete_request(self, mock_call_webhook: MagicMock):
        """Test that webhook is called for DELETE requests to regular endpoints."""
        mock_call_webhook.return_value = AsyncMock()

        with webhook_config(), test_client_context() as client:
            # Make a DELETE request to a non-filtered endpoint
            # Use a valid UUID to avoid validation errors
            test_uuid = str(uuid.uuid4())
            client.delete(f"/api/data_products/{test_uuid}")

        # Verify webhook was called
        assert mock_call_webhook.called

    @patch("app.main.call_webhook")
    def test_webhook_not_called_for_get_request(self, mock_call_webhook: MagicMock):
        """Test that webhook is NOT called for GET requests."""
        mock_call_webhook.return_value = AsyncMock()

        with webhook_config(), test_client_context() as client:
            # Make a GET request
            client.get("/api/data_products")

        # Verify webhook was NOT called
        assert not mock_call_webhook.called

    @patch("app.main.call_webhook")
    def test_webhook_not_called_for_api_auth_path(self, mock_call_webhook: MagicMock):
        """Test that webhook is NOT called for /api/auth/ paths."""
        mock_call_webhook.return_value = AsyncMock()

        with webhook_config(), test_client_context() as client:
            # Make a POST request to /api/auth/ endpoint
            client.post(
                "/api/auth/login",
                json={"username": "test", "password": "test"},
            )

        # Verify webhook was NOT called
        assert not mock_call_webhook.called

    @patch("app.main.call_webhook")
    def test_webhook_not_called_for_api_v2_authn_path(
        self, mock_call_webhook: MagicMock
    ):
        """Test that webhook is NOT called for /api/v2/authn/ paths."""
        mock_call_webhook.return_value = AsyncMock()

        with webhook_config(), test_client_context() as client:
            # Make a POST request to /api/v2/authn/ endpoint
            client.post(
                "/api/v2/authn/device-code",
                json={"client_id": "test"},
            )

        # Verify webhook was NOT called
        assert not mock_call_webhook.called

    @patch("app.main.call_webhook")
    def test_webhook_not_called_for_api_v2_authn_subpath(
        self, mock_call_webhook: MagicMock
    ):
        """Test that webhook is NOT called for any subpath under /api/v2/authn/."""
        mock_call_webhook.return_value = AsyncMock()

        with webhook_config(), test_client_context() as client:
            # Make a PUT request to a subpath of /api/v2/authn/
            client.put(
                "/api/v2/authn/device-code/some-id",
                json={"status": "approved"},
            )

        # Verify webhook was NOT called
        assert not mock_call_webhook.called

    @patch("app.main.call_webhook")
    def test_webhook_not_called_when_url_not_configured(
        self, mock_call_webhook: MagicMock
    ):
        """Test that webhook is NOT called when WEBHOOK_URL is not configured."""
        mock_call_webhook.return_value = AsyncMock()

        with webhook_config(webhook_url=None), test_client_context() as client:
            # Make a POST request
            client.post(
                "/api/data_products",
                json={"name": "test"},
            )

        # Verify webhook was NOT called
        assert not mock_call_webhook.called

    @patch("app.main.call_webhook")
    def test_webhook_receives_correct_parameters(self, mock_call_webhook: MagicMock):
        """Test that webhook receives correct parameters."""
        mock_call_webhook.return_value = AsyncMock()

        with webhook_config(), test_client_context() as client:
            # Make a POST request
            test_payload = {"name": "test-product"}
            client.post(
                "/api/data_products?param=value",
                json=test_payload,
            )

        # Verify webhook was called with correct parameters
        assert mock_call_webhook.called
        call_args = mock_call_webhook.call_args

        # Check that the webhook was called with the expected arguments
        assert call_args.kwargs["method"] == "POST"
        assert call_args.kwargs["url"] == "/api/data_products"
        assert call_args.kwargs["query"] == "param=value"
        assert "status_code" in call_args.kwargs
