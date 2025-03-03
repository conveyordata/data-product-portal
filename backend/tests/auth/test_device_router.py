from base64 import b64encode
from time import sleep

ENDPOINT = "/api/auth/device"


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
        sleep(5)  # Avoids hitting the SlowdownException
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
