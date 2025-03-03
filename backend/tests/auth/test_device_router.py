from base64 import b64encode
from time import sleep
from unittest.mock import patch

import pytest

ENDPOINT = "/api/auth/device"


@pytest.fixture
def mock_oidc_config_monkey():
    with patch("app.core.auth.oidc.OIDCConfiguration", autospec=True) as MockOIDC:
        mock_instance = MockOIDC.return_value  # Mocked instance
        mock_instance.client_id = "test_client_id"
        mock_instance.client_secret = "test_client_secret"
        mock_instance.redirect_uri = "http://test-redirect-uri"
        mock_instance.token_endpoint = "http://test-token-endpoint"
        mock_instance.authorization_endpoint = "http://test-authorization-endpoint"
        mock_instance.provider = "test-provider"
        from app.core.auth import jwt

        jwt.oidc = mock_instance  # Override existing `oidc` instance in `jwt.py`

        yield mock_instance


class TestAuthDeviceRouter:
    @staticmethod
    def basic_auth(username, password):
        token = b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
        return f"Basic {token}"

    def test_get_device_token(self, client):
        response = client.post(f"{ENDPOINT}/device_token?client_id=test")
        assert response.status_code == 200
        assert response.json()["oidc_redirect_uri"] == "http://test-redirect-uri"
        assert response.json()["status"] == "authorization_pending"

    def test_get_jwt_token(self, client):
        response = client.post(f"{ENDPOINT}/device_token?client_id=test")
        device_code = response.json()["device_code"]
        sleep(5)
        response = client.post(
            f"{ENDPOINT}/jwt_token?"
            f"client_id=test&device_code={device_code}"
            "&grant_type=urn:ietf:params:oauth:"
            "grant-type:device_code"
        )
        assert response.status_code == 400  # user has not yet authorized
        # TODO Test other flows

    def test_get_root(self, client):
        response = client.post(f"{ENDPOINT}/device_token?client_id=test")
        user_code = response.json()["user_code"]
        response = client.get(f"{ENDPOINT}/?code={user_code}")
        assert response.status_code == 200

    def test_get_allow(self, client):
        response = client.post(f"{ENDPOINT}/device_token?client_id=test")
        device_code = response.json()["device_code"]
        response = client.get(
            f"{ENDPOINT}/allow?client_id=test&device_code={device_code}"
        )
        assert response.status_code == 200

    def test_get_deny(self, client):
        response = client.post(f"{ENDPOINT}/device_token?client_id=test")
        device_code = response.json()["device_code"]
        response = client.get(
            f"{ENDPOINT}/deny?client_id=test&device_code={device_code}"
        )
        assert response.status_code == 200

    def test_get_callback(self, client):
        response = client.get(f"{ENDPOINT}/callback?code=test&state=test")
        assert response.status_code == 200
