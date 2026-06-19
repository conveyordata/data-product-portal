from base64 import b64encode
from datetime import timedelta
from urllib.parse import parse_qs, urlparse

from freezegun import freeze_time

from app.core.auth.device_flows.model import DeviceFlow
from app.database.database import get_db_session

ENDPOINT = "/api/v2/authn/device"


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
        with freeze_time("2023-01-01 12:00:00") as frozen_datetime:
            response = client.post(f"{ENDPOINT}/device_token?client_id=test")
            device_code = response.json()["device_code"]
            frozen_datetime.tick(delta=timedelta(seconds=6))
            response = client.post(
                f"{ENDPOINT}/jwt_token?"
                f"client_id=test&device_code={device_code}"
                "&grant_type=urn:ietf:params:oauth:"
                "grant-type:device_code"
            )
            assert response.status_code == 400  # user has not yet authorized

    def test_get_root(self, client):
        response = client.post(f"{ENDPOINT}/device_token?client_id=test")
        user_code = response.json()["user_code"]
        response = client.get(f"{ENDPOINT}/?code={user_code}")
        assert response.status_code == 200

    def test_get_allow(self, client):
        response = client.post(f"{ENDPOINT}/device_token?client_id=test")
        device_code = response.json()["device_code"]
        response = client.get(
            f"{ENDPOINT}/allow?client_id=test&device_code={device_code}",
            follow_redirects=False,
        )
        assert response.status_code == 302, response.text

        location = response.headers["location"]
        parsed = urlparse(location)
        params = parse_qs(parsed.query)

        assert parsed.scheme == "http"
        assert parsed.netloc == "test-authorization-endpoint"
        assert params["response_type"] == ["code"]
        assert params["client_id"] == ["test"]
        assert params["code_challenge_method"] == ["S256"]
        assert params["identity_provider"] == ["test-provider"]
        assert params["redirect_uri"] == [
            "http://test-redirect-uri/api/v2/authn/device/callback"
        ]

    def test_get_deny(self, client):
        response = client.post(f"{ENDPOINT}/device_token?client_id=test")
        device_code = response.json()["device_code"]
        response = client.get(
            f"{ENDPOINT}/deny?client_id=test&device_code={device_code}",
            follow_redirects=False,
        )
        assert response.status_code == 307, response.text
        assert response.headers["location"] == "/"

    def test_get_callback(self, client):
        db_session = next(get_db_session())
        mock_device = DeviceFlow(
            authz_state="test",
        )
        db_session.add(mock_device)
        db_session.commit()

        response = client.get(f"{ENDPOINT}/callback?code=test&state=test")
        assert response.status_code == 200
