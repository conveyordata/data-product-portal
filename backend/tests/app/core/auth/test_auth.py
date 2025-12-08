import importlib
from unittest.mock import patch

import pytest
from fastapi import HTTPException, status

from app.settings import settings


@pytest.fixture
def force_oidc_enabled():
    """Force OIDC_ENABLED to be True for testing"""
    settings.OIDC_ENABLED = True

    # Reload the auth module to pick up the new setting
    import app.core.auth.auth

    importlib.reload(app.core.auth.auth)
    yield
    settings.OIDC_ENABLED = False
    # Reload the auth module to pick up the new setting
    import app.core.auth.auth

    importlib.reload(app.core.auth.auth)


class TestCoreAuthentication:
    def test_api_key_authenticated_no_api_key_no_jwt_raises_403(
        self, force_oidc_enabled
    ):
        """Test that when both api_key and jwt_token are None, it raises 403"""
        from app.core.auth.auth import api_key_authenticated

        with pytest.raises(HTTPException) as exc_info:
            api_key_authenticated(api_key=None, jwt_token=None)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Unauthenticated"

    @patch("app.core.auth.auth.secured_call")
    def test_api_key_authenticated_no_api_key_with_jwt_calls_secured_call(
        self, mock_secured_call, force_oidc_enabled
    ):
        """Test that when api_key is None but jwt_token exists, it calls secured_call"""
        from app.core.auth.auth import JWTToken, api_key_authenticated

        mock_jwt_token = "test_jwt_token"
        mock_secured_call.return_value = JWTToken(sub="test_user", token=mock_jwt_token)

        result = api_key_authenticated(api_key=None, jwt_token=mock_jwt_token)

        mock_secured_call.assert_called_once_with(mock_jwt_token)
        assert result.sub == "test_user"
        assert result.token == mock_jwt_token

    def test_api_key_authenticated_with_api_key_returns_system_account(
        self, force_oidc_enabled
    ):
        """Test that when api_key is provided, it returns system account token"""
        from app.core.auth.auth import api_key_authenticated

        mock_api_key = "valid_api_key"

        result = api_key_authenticated(api_key=mock_api_key, jwt_token=None)

        assert result.sub == "systemaccount_bot"
        assert result.token == ""

    def test_api_key_authenticated_with_both_api_key_and_jwt_prefers_api_key(
        self, force_oidc_enabled
    ):
        """Test that when both api_key and jwt_token are provided, it uses api_key"""
        from app.core.auth.auth import api_key_authenticated

        mock_api_key = "valid_api_key"
        mock_jwt_token = "test_jwt_token"

        result = api_key_authenticated(api_key=mock_api_key, jwt_token=mock_jwt_token)

        assert result.sub == "systemaccount_bot"
        assert result.token == ""

    def test_api_key_authenticated_empty_string_api_key_with_jwt(
        self, force_oidc_enabled
    ):
        """Test that empty string api_key is treated as falsy and uses JWT"""
        from app.core.auth.auth import JWTToken, api_key_authenticated

        with patch("app.core.auth.auth.secured_call") as mock_secured_call:
            mock_jwt_token = "test_jwt_token"
            mock_secured_call.return_value = JWTToken(
                sub="test_user", token=mock_jwt_token
            )

            result = api_key_authenticated(api_key="", jwt_token=mock_jwt_token)

            mock_secured_call.assert_called_once_with(mock_jwt_token)
            assert result.sub == "test_user"
