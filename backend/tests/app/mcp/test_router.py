from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.mcp.router import router


@pytest.fixture
def test_client():
    """Create a test client with the MCP router."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def mock_oidc():
    """Mock OIDC configuration."""
    mock = Mock()
    mock.authority = "https://auth.example.com"
    mock.authorization_endpoint = "https://auth.example.com/auth"
    mock.token_endpoint = "https://auth.example.com/token"
    mock.jwks_uri = "https://auth.example.com/.well-known/jwks"
    mock.client_id = "test-client-id"
    mock.client_secret = "test-client-secret"
    return mock


@pytest.fixture
def mock_settings():
    """Mock settings configuration."""
    mock = Mock()
    mock.HOST = "https://api.example.com/"
    return mock


class TestOAuthMetadata:
    """Test cases for oauth_metadata endpoint."""

    @patch("app.mcp.router.get_oidc")
    @patch("app.mcp.router.settings")
    def test_oauth_metadata_success(
        self, mock_settings, mock_get_oidc, test_client, mock_oidc
    ):
        """Test successful OAuth metadata response."""
        mock_get_oidc.return_value = mock_oidc
        mock_settings.HOST = "https://api.example.com/"

        response = test_client.get("/.well-known/oauth-authorization-server")

        assert response.status_code == 200
        data = response.json()
        assert data["issuer"] == "https://auth.example.com"
        assert data["authorization_endpoint"] == "https://auth.example.com/auth"
        assert data["token_endpoint"] == "https://auth.example.com/token"
        assert data["jwks_uri"] == "https://auth.example.com/.well-known/jwks"
        assert data["registration_endpoint"] == "https://api.example.com/api/register"
        assert data["response_types_supported"] == ["code"]
        assert data["code_challenge_methods_supported"] == ["S256"]
        assert data["token_endpoint_auth_methods_supported"] == ["client_secret_post"]
        assert data["grant_types_supported"] == ["authorization_code", "refresh_token"]

    @patch("app.mcp.router.get_oidc")
    @patch("app.mcp.router.settings")
    def test_oauth_metadata_with_trailing_slash(
        self, mock_settings, mock_get_oidc, test_client, mock_oidc
    ):
        """Test OAuth metadata with trailing slash in HOST."""
        mock_get_oidc.return_value = mock_oidc
        mock_settings.HOST = "https://api.example.com/"

        response = test_client.get("/.well-known/oauth-authorization-server")

        assert response.status_code == 200
        data = response.json()
        assert data["registration_endpoint"] == "https://api.example.com/api/register"


class TestOpenIDConfig:
    """Test cases for openid_config endpoint."""

    @patch("app.mcp.router.get_oidc")
    def test_openid_config_success(self, mock_get_oidc, test_client, mock_oidc):
        """Test successful OpenID configuration response."""
        mock_get_oidc.return_value = mock_oidc

        response = test_client.get("/.well-known/openid-configuration")

        assert response.status_code == 200
        data = response.json()
        assert data["issuer"] == "https://auth.example.com"
        assert data["authorization_endpoint"] == "https://auth.example.com/auth"
        assert data["token_endpoint"] == "https://auth.example.com/token"
        assert data["jwks_uri"] == "https://auth.example.com/.well-known/jwks"
        assert data["response_types_supported"] == ["code"]
        assert data["subject_types_supported"] == ["public"]
        assert data["id_token_signing_alg_values_supported"] == ["RS256"]


class TestOAuthProtectedResource:
    """Test cases for oauth_protected_resource endpoint."""

    @patch("app.mcp.router.get_oidc")
    @patch("app.mcp.router.settings")
    def test_oauth_protected_resource_main_endpoint(
        self, mock_settings, mock_get_oidc, test_client, mock_oidc
    ):
        """Test OAuth protected resource metadata from main endpoint."""
        mock_get_oidc.return_value = mock_oidc
        mock_settings.HOST = "https://api.example.com/"

        response = test_client.get("/.well-known/oauth-protected-resource")

        assert response.status_code == 200
        data = response.json()
        assert data["resource"] == "https://api.example.com/"
        assert data["authorization_servers"] == ["https://api.example.com/"]
        assert data["jwks_uri"] == "https://auth.example.com/.well-known/jwks"
        assert data["bearer_methods_supported"] == ["header"]
        assert data["resource_documentation"] == "https://api.example.com/docs"

    @patch("app.mcp.router.get_oidc")
    @patch("app.mcp.router.settings")
    def test_oauth_protected_resource_mcp_endpoint(
        self, mock_settings, mock_get_oidc, test_client, mock_oidc
    ):
        """Test OAuth protected resource metadata from MCP-specific endpoint."""
        mock_get_oidc.return_value = mock_oidc
        mock_settings.HOST = "https://api.example.com"

        response = test_client.get("/.well-known/oauth-protected-resource/mcp/mcp")

        assert response.status_code == 200
        data = response.json()
        assert data["resource"] == "https://api.example.com/"
        assert data["authorization_servers"] == ["https://api.example.com/"]

    @patch("app.mcp.router.get_oidc")
    @patch("app.mcp.router.settings")
    def test_oauth_protected_resource_no_trailing_slash(
        self, mock_settings, mock_get_oidc, test_client, mock_oidc
    ):
        """Test OAuth protected resource with HOST without trailing slash."""
        mock_get_oidc.return_value = mock_oidc
        mock_settings.HOST = "https://api.example.com"

        response = test_client.get("/.well-known/oauth-protected-resource")

        assert response.status_code == 200
        data = response.json()
        assert data["resource"] == "https://api.example.com/"


class TestRegister:
    """Test cases for register endpoint."""

    @patch("app.mcp.router.time.time")
    @patch("app.mcp.router.logger")
    @patch("app.mcp.router.get_oidc")
    @patch("app.mcp.router.settings")
    def test_register_success_minimal_data(
        self,
        mock_settings,
        mock_get_oidc,
        mock_logger,
        mock_time,
        test_client,
        mock_oidc,
    ):
        """Test successful registration with minimal data."""
        mock_get_oidc.return_value = mock_oidc
        mock_settings.HOST = "https://api.example.com/"
        mock_time.return_value = 1234567890

        request_data = {}

        response = test_client.post("/api/register", json=request_data)

        assert response.status_code == 201
        data = response.json()
        assert data["client_id"] == "test-client-id"
        assert data["client_secret"] == "test-client-secret"
        assert data["client_id_issued_at"] == 1234567890
        assert data["client_secret_expires_at"] == 0
        assert data["redirect_uris"] == ["https://api.example.com"]
        assert data["token_endpoint_auth_method"] == "client_secret_post"
        assert data["grant_types"] == ["authorization_code"]
        assert data["response_types"] == ["code"]
        assert data["client_name"] == ""
        assert data["scope"] == ""

        # Verify logging was called
        mock_logger.info.assert_called()

    @patch("app.mcp.router.time.time")
    @patch("app.mcp.router.logger")
    @patch("app.mcp.router.get_oidc")
    @patch("app.mcp.router.settings")
    def test_register_success_full_data(
        self,
        mock_settings,
        mock_get_oidc,
        mock_logger,
        mock_time,
        test_client,
        mock_oidc,
    ):
        """Test successful registration with full data."""
        mock_get_oidc.return_value = mock_oidc
        mock_settings.HOST = "https://api.example.com"
        mock_time.return_value = 1234567890

        request_data = {
            "token_endpoint_auth_method": "client_secret_basic",
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code", "token"],
            "client_name": "Test Client",
            "scope": "openid profile",
        }

        response = test_client.post("/api/register", json=request_data)

        assert response.status_code == 201
        data = response.json()
        assert data["token_endpoint_auth_method"] == "client_secret_basic"
        assert data["grant_types"] == ["authorization_code", "refresh_token"]
        assert data["response_types"] == ["code", "token"]
        assert data["client_name"] == "Test Client"
        assert data["scope"] == "openid profile"
        assert data["redirect_uris"] == ["https://api.example.com"]

    @patch("app.mcp.router.logger")
    def test_register_header_redaction(self, mock_logger, test_client):
        """Test that sensitive headers are redacted in logs."""
        headers = {
            "authorization": "Bearer secret-token",
            "cookie": "session=secret",
            "content-type": "application/json",
        }

        test_client.post("/api/register", json={}, headers=headers)

        # Verify sensitive headers were redacted
        logged_calls = [
            call[0][0]
            for call in mock_logger.info.call_args_list
            if "/register headers:" in call[0][0]
        ]
        assert len(logged_calls) > 0
        logged_headers = logged_calls[0]
        assert "[REDACTED]" in logged_headers
        assert "secret-token" not in logged_headers
        assert "secret" not in logged_headers
        assert "application/json" in logged_headers

    @patch("app.mcp.router.logger")
    def test_register_invalid_json(self, mock_logger, test_client):
        """Test registration with invalid JSON body."""
        response = test_client.post("/api/register", data="invalid json")

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "Invalid JSON body"

        # Verify error was logged
        mock_logger.error.assert_called()
        error_call = mock_logger.error.call_args[0][0]
        assert "Failed to parse JSON body" in error_call

    @patch("app.mcp.router.logger")
    def test_register_privacy_logging(self, mock_logger, test_client):
        """Test that registration data is not logged for privacy."""
        request_data = {"client_name": "Secret Client", "scope": "secret-scope"}

        response = test_client.post("/api/register", json=request_data)

        assert response.status_code == 201

        # Verify that sensitive data is not in logs
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        privacy_call = next(
            (call for call in info_calls if "fields redacted for privacy" in call), None
        )
        assert privacy_call is not None

        # Verify actual data is not logged
        all_log_text = " ".join(info_calls)
        assert "Secret Client" not in all_log_text
        assert "secret-scope" not in all_log_text

    @patch("app.mcp.router.logger")
    def test_register_set_cookie_header_redaction(self, mock_logger, test_client):
        """Test that set-cookie header is also redacted."""
        headers = {"set-cookie": "secret-cookie=value"}

        test_client.post("/api/register", json={}, headers=headers)

        logged_calls = [
            call[0][0]
            for call in mock_logger.info.call_args_list
            if "/register headers:" in call[0][0]
        ]
        assert len(logged_calls) > 0
        logged_headers = logged_calls[0]
        assert "[REDACTED]" in logged_headers
        assert "secret-cookie" not in logged_headers

    @patch("app.mcp.router.logger")
    def test_register_case_insensitive_header_redaction(self, mock_logger, test_client):
        """Test that header redaction works case-insensitively."""
        headers = {"Authorization": "Bearer token", "Cookie": "session=value"}

        test_client.post("/api/register", json={}, headers=headers)

        logged_calls = [
            call[0][0]
            for call in mock_logger.info.call_args_list
            if "/register headers:" in call[0][0]
        ]
        assert len(logged_calls) > 0
        logged_headers = logged_calls[0]
        # Should be redacted due to case-insensitive matching
        assert "[REDACTED]" in logged_headers
