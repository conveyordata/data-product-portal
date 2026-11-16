import asyncio
from types import SimpleNamespace
from unittest.mock import patch

import jwt as pyjwt
import pytest

from app.mcp.deps import PortalOIDCProxy, get_mcp_authenticated_user
from app.settings import settings
from tests.factories import UserFactory

ENTRA_ID_TOKEN = {
    "sub": "entra-pairwise-sub-1",
    "oid": "object-id-1",
    "email": "anna@contoso.com",
    "name": "Anna van Dijk",
}


@pytest.fixture
def user_id_claim(monkeypatch):
    monkeypatch.setattr(settings, "OIDC_ENABLED", True)
    monkeypatch.setattr(settings, "OIDC_USER_ID_CLAIM", "oid")


def mcp_access_token(upstream_claims):
    return SimpleNamespace(
        claims={"upstream_claims": upstream_claims}, client_id="mcp", scopes=[]
    )


class TestMcpUserIdClaim:
    def test_extract_upstream_claims__keeps_configured_user_id_claim(
        self, user_id_claim
    ):
        id_token = pyjwt.encode(ENTRA_ID_TOKEN, "secret", algorithm="HS256")

        claims = asyncio.run(
            PortalOIDCProxy._extract_upstream_claims(None, {"id_token": id_token})
        )

        assert claims["oid"] == "object-id-1"

    def test_get_mcp_authenticated_user__looks_up_configured_user_id_claim(
        self, user_id_claim, session
    ):
        user = UserFactory(external_id="object-id-1")
        token = mcp_access_token(ENTRA_ID_TOKEN)

        with patch("app.mcp.deps.get_access_token", return_value=token):
            found = get_mcp_authenticated_user(db=session)

        assert found.id == user.id

    def test_get_mcp_authenticated_user__missing_user_id_claim_is_rejected(
        self, user_id_claim, session
    ):
        UserFactory(external_id="entra-pairwise-sub-1")
        token = mcp_access_token({"sub": "entra-pairwise-sub-1"})

        with (
            patch("app.mcp.deps.get_access_token", return_value=token),
            pytest.raises(ValueError, match="missing 'oid'"),
        ):
            get_mcp_authenticated_user(db=session)
