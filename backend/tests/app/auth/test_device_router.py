import importlib
from base64 import b64encode
from datetime import timedelta
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time
from starlette.routing import _DefaultLifespan

from app.core.auth.device_flows.service import verify_auth_header
from app.database.database import get_system_db_session
from app.settings import settings
from tests.conftest import override_unauthenticated_get_db
from tests.factories import DeviceFlowFactory

ENDPOINT = "/api/v2/authn/device"


@pytest.fixture(params=["oidc_disabled", "oidc_enabled"])
def oidc_enabled_client(request):
    """
    Runs every test in this file twice: once as before (OIDC disabled, the
    default in this test suite), and once with OIDC actually enabled, which
    is what production runs with. That means get_authenticated_user really
    requires a valid API key or JWT here. If a device-flow route depends on
    get_db_session instead of get_system_db_session, it needs an
    authenticated user and this second run will fail with 401/403, exactly
    as it would in production.
    """
    oidc_enabled = request.param == "oidc_enabled"
    modules = [
        importlib.import_module("app.core.auth.auth"),
        importlib.import_module("app.database.deps"),
        importlib.import_module("app.core.auth.device_flows.router"),
        importlib.import_module("app.core.auth.router"),
        importlib.import_module("app.main"),
    ]

    if oidc_enabled:
        settings.OIDC_ENABLED = True
        for module in modules:
            importlib.reload(module)

    app = modules[-1].app
    app.router.lifespan_context = _DefaultLifespan(app.router)
    app.dependency_overrides[get_system_db_session] = override_unauthenticated_get_db
    app.dependency_overrides[verify_auth_header] = lambda: "test"

    with TestClient(app) as test_client:
        yield test_client
        app.dependency_overrides.clear()

    if oidc_enabled:
        settings.OIDC_ENABLED = False
        for module in modules:
            importlib.reload(module)


class TestAuthDeviceRouter:
    @staticmethod
    def basic_auth(username, password):
        token = b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
        return f"Basic {token}"

    def test_get_device_token(self, oidc_enabled_client):
        response = oidc_enabled_client.post(f"{ENDPOINT}/device_token?client_id=test")
        assert response.status_code == 200, response.text
        assert response.json()["oidc_redirect_uri"] == "http://test-redirect-uri"
        assert response.json()["status"] == "authorization_pending"

    def test_get_jwt_token(self, oidc_enabled_client):
        with freeze_time("2023-01-01 12:00:00") as frozen_datetime:
            response = oidc_enabled_client.post(
                f"{ENDPOINT}/device_token?client_id=test"
            )
            device_code = response.json()["device_code"]
            frozen_datetime.tick(delta=timedelta(seconds=6))
            response = oidc_enabled_client.post(
                f"{ENDPOINT}/jwt_token?"
                f"client_id=test&device_code={device_code}"
                "&grant_type=urn:ietf:params:oauth:"
                "grant-type:device_code"
            )
            assert response.status_code == 400  # user has not yet authorized

    def test_get_root(self, oidc_enabled_client):
        response = oidc_enabled_client.post(f"{ENDPOINT}/device_token?client_id=test")
        user_code = response.json()["user_code"]
        response = oidc_enabled_client.get(f"{ENDPOINT}/?code={user_code}")
        assert response.status_code == 200

    def test_get_allow(self, oidc_enabled_client):
        response = oidc_enabled_client.post(f"{ENDPOINT}/device_token?client_id=test")
        device_code = response.json()["device_code"]
        response = oidc_enabled_client.get(
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

    def test_get_deny(self, oidc_enabled_client):
        response = oidc_enabled_client.post(f"{ENDPOINT}/device_token?client_id=test")
        device_code = response.json()["device_code"]
        response = oidc_enabled_client.get(
            f"{ENDPOINT}/deny?client_id=test&device_code={device_code}",
            follow_redirects=False,
        )
        assert response.status_code == 307, response.text
        assert response.headers["location"] == "/"

    def test_get_callback(self, oidc_enabled_client, session):
        DeviceFlowFactory(
            authz_state="test",
        )
        response = oidc_enabled_client.get(f"{ENDPOINT}/callback?code=test&state=test")
        assert response.status_code == 200
