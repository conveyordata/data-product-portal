import base64
import time
import webbrowser
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests


class DeviceFlowClient:
    """Client for OAuth Device Flow authentication"""

    def __init__(self, base_url: str, client_id: str, auth_client_id: str):
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.auth_client_id = auth_client_id
        self.auth_token = base64.b64encode(
            f"{client_id}:{auth_client_id}".encode()
        ).decode()
        self.device_endpoint = urljoin(self.base_url, "/api/auth/device")

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests"""
        return {
            "Authorization": f"Basic {self.auth_token}",
            "Content-Type": "application/json",
        }

    def get_device_token(self, scope: str = "openid") -> Dict[str, Any]:
        """
        Step 1: Request a device token from the authorization server

        Returns:
            Dict containing device_code, user_code, verification_uri, etc.
        """
        url = f"{self.device_endpoint}/device_token"

        data = {"client_id": self.client_id, "scope": scope}

        response = requests.post(url, params=data, headers=self._get_auth_headers())
        response.raise_for_status()
        return response.json()

    def poll_for_jwt_token(
        self, device_code: str, interval: int = 5, timeout: int = 300
    ) -> Optional[Dict[str, Any]]:
        """
        Step 3: Poll for JWT token after user authorization

        Args:
            device_code: The device code from get_device_token()
            interval: Polling interval in seconds
            timeout: Maximum time to wait in seconds

        Returns:
            Dict containing access_token and other token info, or None if timeout
        """
        url = f"{self.device_endpoint}/jwt_token"

        data = {
            "client_id": self.client_id,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        }

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = requests.post(
                    url, params=data, headers=self._get_auth_headers()
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 400:
                    error_data = response.json()
                    error = error_data.get("error", "")

                    if error == "authorization_pending":
                        print("Authorization pending, continuing to poll...")
                        time.sleep(interval)
                        continue
                    elif error == "slow_down":
                        print("Slowing down polling interval...")
                        interval = min(
                            interval + 5, 30
                        )  # Increase interval but cap at 30s
                        time.sleep(interval)
                        continue
                    elif error in ["access_denied", "expired_token"]:
                        print(f"Authorization failed: {error}")
                        return None
                    else:
                        print(f"Unexpected error: {error}")
                        return None
                else:
                    response.raise_for_status()

            except requests.RequestException as e:
                print(f"Request failed: {e}")
                time.sleep(interval)
                continue

        print("Timeout waiting for user authorization")
        return None

    def authenticate(
        self, scope: str = "openid", open_browser: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Complete device flow authentication process

        Args:
            scope: OAuth scope to request
            open_browser: Whether to automatically open the verification URL

        Returns:
            Dict containing access_token and other token info, or None if failed
        """
        print("Starting OAuth Device Flow authentication...")

        # Step 1: Get device token
        try:
            device_response = self.get_device_token(scope)
            print("Device token obtained successfully")
        except requests.RequestException as e:
            print(f"Failed to get device token: {e}")
            return None

        # Step 2: Display user instructions
        user_code = device_response.get("user_code")
        verification_uri = device_response.get("verification_uri_complete")
        device_code: str = str(device_response.get("device_code"))
        expires_in: int = device_response.get("expires_in", 300)
        interval: int = device_response.get("interval", 5)

        print("\nTo authorize this application:")
        print(f"1. Go to: {verification_uri}")
        print(f"2. Enter code: {user_code}")
        print(f"3. Code expires in {expires_in} seconds")

        if open_browser and verification_uri:
            print("Opening browser automatically...")
            webbrowser.open(verification_uri)

        # Step 3: Poll for token
        print("\nWaiting for authorization...")
        return self.poll_for_jwt_token(device_code, interval, expires_in)
