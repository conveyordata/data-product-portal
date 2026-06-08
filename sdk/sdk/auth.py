import json
import logging
import os
import time
from pathlib import Path
from typing import Optional, cast
from urllib.parse import urlencode

import httpx

from sdk.api_client.api.authentication import get_device_token, get_jwt_token
from sdk.api_client.client import AuthenticatedClient, Client
from sdk.api_client.models import DeviceFlow, DeviceFlowStatus

logger = logging.getLogger(__name__)
TOKEN_PATH = Path.home() / ".portal" / "token.json"


class PortalAuth:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.auth_mode = os.getenv("PORTAL_AUTH_MODE", "")
        self.base_url = os.getenv("PORTAL_BASE_URL", "").rstrip("/")
        self.client_id = os.getenv("PORTAL_CLIENT_ID", "")
        self.client_secret = os.getenv("PORTAL_CLIENT_SECRET", "")
        self.token_url = os.getenv("PORTAL_TOKEN_URL", "")
        self.scope = os.getenv("PORTAL_SCOPE", "openid")
        self.dev_mode = os.getenv("PORTAL_DEV_MODE", "false").lower()

        if not all([self.client_id, self.client_secret, self.base_url]):
            raise ValueError("Missing required PORTAL_* environment variables")

        self._token = self._load_token()

    @staticmethod
    def _load_token() -> Optional[dict]:
        if not TOKEN_PATH.exists():
            return None

        with TOKEN_PATH.open() as f:
            return json.load(f)

    @staticmethod
    def _save_token(token: dict) -> None:
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with TOKEN_PATH.open("w") as f:
            json.dump(token, f, indent=2)

    @staticmethod
    def _clear_token() -> None:
        TOKEN_PATH.unlink(missing_ok=True)

    def _is_token_valid(self) -> bool:
        if not self._token:
            return False
        return time.time() < self._token["expires_at"] - 30

    def get_access_token(self) -> str:
        if self.dev_mode == "true":
            return ""
        if self._is_token_valid():
            return self._token["access_token"]  # type: ignore

        if self.auth_mode == "client_credentials":
            self._client_credentials_login()
        else:
            if not (self._token and "refresh_token" in self._token and self._refresh()):
                self._device_login()

        return self._token["access_token"]  # type: ignore

    def _client_credentials_login(self):
        if not self.client_secret:
            raise RuntimeError(
                "Client credentials requested but PORTAL_CLIENT_SECRET is missing"
            )

        response = httpx.post(
            self.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": self.scope,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=self.timeout,
        )

        if not response.is_success:
            raise RuntimeError(f"Client credentials auth failed: {response.text}")
        else:
            logger.info("Successfully authenticated")
            token_body = response.json()
            self._store_token_response(token_body, persist=False)

    def _device_login(self) -> None:
        client = cast(
            AuthenticatedClient,
            Client(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
                httpx_args={
                    "auth": httpx.BasicAuth(self.client_id, self.client_secret)
                },
            ),
        )

        response = get_device_token.sync_detailed(client=client, scope=self.scope)
        if not (200 <= response.status_code < 300):
            raise RuntimeError(f"Device authorization failed: {response.status_code}")

        payload: DeviceFlow = cast(DeviceFlow, response.parsed)
        device_code = payload.device_code
        user_code = payload.user_code
        verification_uri = payload.verification_uri_complete
        interval = payload.interval or 5
        expires_in = payload.expiration or 900

        print("\n🔐 Authorization required")
        print(f"➡  Visit: {verification_uri}")
        print(f"➡  Enter code: {user_code}\n")

        deadline = time.time() + expires_in
        while time.time() < deadline:
            time.sleep(interval)

            token_response = get_jwt_token.sync_detailed(
                client=client,
                device_code=str(device_code),
                grant_type="urn:ietf:params:oauth:grant-type:device_code",
            )
            if token_response.status_code == 200:
                self._store_token_response(
                    json.loads(token_response.content), persist=True
                )
                return

            jwt_data = json.loads(token_response.content)
            detail = jwt_data.get("detail")
            if detail == DeviceFlowStatus.AUTHORIZATION_PENDING:
                logger.debug("The user has not authorized the challenge.")
                continue
            elif detail == DeviceFlowStatus.DENIED:
                raise RuntimeError("Verification request was denied")
            elif detail == DeviceFlowStatus.EXPIRED:
                logger.debug("The challenge was expired.")
                break
            else:
                logger.debug(f"Unexpected status: {detail}")
                continue

        raise TimeoutError("Device authorization timed out")

    def _refresh(self) -> bool:
        params = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": self._token["refresh_token"],  # type: ignore
        }
        response = httpx.post(
            self.token_url,
            auth=httpx.BasicAuth(self.client_id, self.client_secret),
            data=urlencode(params),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=self.timeout,
        )

        if not response.is_success:
            return False

        payload = response.json()
        self._store_token_response(payload, persist=True, keep_refresh=True)
        return True

    def _store_token_response(
        self, payload: dict, persist: bool, keep_refresh: bool = False
    ) -> None:
        expires_in = payload.get("expires_in", 3600)

        token = {
            "access_token": payload["access_token"],
            "expires_at": time.time() + expires_in,
        }

        if keep_refresh and self._token and "refresh_token" in self._token:
            token["refresh_token"] = self._token["refresh_token"]
        elif "refresh_token" in payload:
            token["refresh_token"] = payload["refresh_token"]

        self._token = token
        if persist:
            self._save_token(token)
