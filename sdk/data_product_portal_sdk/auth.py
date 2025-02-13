import time
import webbrowser
from base64 import b64encode

from data_product_portal_sdk.data_product_portal_client import Client
from data_product_portal_sdk.data_product_portal_client.api.auth import (
    get_device_token_api_auth_device_device_token_post,
    get_jwt_token_api_auth_device_jwt_token_post,
)
from data_product_portal_sdk.data_product_portal_client.models import DeviceFlow
from httpx import HTTPStatusError


def basic_auth(username, password):
    token = b64encode(f"{username}:{password}".encode()).decode("ascii")
    return f"Basic {token}"


class PortalClient:
    def __init__(
        self,
        base_url: str,
        client_id: str = "",
        client_secret: str = "",
        headers: dict = None,
    ):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.headers = headers or {}

        if self.client_id and self.client_secret:
            self.headers["Authorization"] = basic_auth(
                self.client_id, self.client_secret
            )

        self.client = Client(base_url=self.base_url, headers=self.headers)

    def __poll_for_jwt_token(self, deviceFlow: DeviceFlow, timeout=300, interval=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                resp = get_jwt_token_api_auth_device_jwt_token_post.sync_detailed(
                    client=self.client,
                    client_id=self.client_id,
                    device_code=deviceFlow.device_code,
                    grant_type="urn:ietf:params:oauth:grant-type:device_code",
                )
                if resp.status_code == 200:
                    return resp
            except HTTPStatusError as e:
                if e.response.status_code == 400:
                    pass
                else:
                    raise e
            time.sleep(interval)
        raise TimeoutError("Polling for JWT token timed out.")

    def __enter__(self):
        if self.client_id and self.client_secret:
            self.__login(self.client)
            self.client = Client(
                base_url=self.base_url,
                headers={
                    **self.headers,
                    "Authorization": f"Bearer {self.access_token}",
                },
            )
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.__exit__(exc_type, exc_val, exc_tb)

    def __login(self, client):
        deviceFlow: DeviceFlow = (
            get_device_token_api_auth_device_device_token_post.sync(
                client=client, client_id=self.client_id
            )
        )
        webbrowser.open(deviceFlow.verification_uri_complete, new=0, autoraise=True)

        resp = self.__poll_for_jwt_token(deviceFlow)
        self.id_token = resp.parsed["id_token"]
        self.access_token = resp.parsed["access_token"]
