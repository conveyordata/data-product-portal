import importlib
import json
import time
from unittest.mock import patch

import httpx
import jwt as pyjwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException, status
from jwt.algorithms import RSAAlgorithm
from sqlalchemy import select

from app.core.auth import jwt as jwt_module
from app.core.auth.auth import SYSTEM_ACCOUNT_BOT_EXTERNAL_ID
from app.settings import settings
from app.users.model import User
from tests.factories import UserFactory


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

        assert result.sub == SYSTEM_ACCOUNT_BOT_EXTERNAL_ID
        assert result.token == ""

    def test_api_key_authenticated_with_both_api_key_and_jwt_prefers_api_key(
        self, force_oidc_enabled
    ):
        """Test that when both api_key and jwt_token are provided, it uses api_key"""
        from app.core.auth.auth import api_key_authenticated

        mock_api_key = "valid_api_key"
        mock_jwt_token = "test_jwt_token"

        result = api_key_authenticated(api_key=mock_api_key, jwt_token=mock_jwt_token)

        assert result.sub == SYSTEM_ACCOUNT_BOT_EXTERNAL_ID
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


ISSUER = "https://idp.example.com"
USERINFO_URL = "https://idp.example.com/userinfo"
KID = "test-kid"
SIGNING_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
OTHER_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def idp(monkeypatch, force_oidc_enabled):
    def configure(audience):
        jwk = json.loads(RSAAlgorithm.to_jwk(SIGNING_KEY.public_key()))
        jwk["kid"] = KID
        monkeypatch.setattr(
            jwt_module.oidc, "jwks_keys", {"keys": [jwk]}, raising=False
        )
        monkeypatch.setattr(jwt_module.oidc, "authority", ISSUER, raising=False)
        monkeypatch.setattr(jwt_module.oidc, "audience", audience, raising=False)
        monkeypatch.setattr(
            jwt_module.oidc, "userinfo_endpoint", USERINFO_URL, raising=False
        )

    return configure


def sign(claims, key=SIGNING_KEY, expires_in=300):
    now = int(time.time())
    payload = {"iss": ISSUER, "iat": now, "exp": now + expires_in, **claims}
    return "Bearer " + pyjwt.encode(
        payload, key, algorithm="RS256", headers={"kid": KID}
    )


def userinfo_returns(status_code, body=None):
    request = httpx.Request("POST", USERINFO_URL)
    if isinstance(body, str):
        response = httpx.Response(status_code, text=body, request=request)
    else:
        response = httpx.Response(status_code, json=body, request=request)
    return patch("app.core.auth.auth.httpx.post", return_value=response)


def log_in(bearer, session):
    from app.core.auth.auth import api_key_authenticated, get_authenticated_user

    token = api_key_authenticated(api_key=None, jwt_token=bearer)
    return get_authenticated_user(token=token, db=session)


def stored_user(session, external_id):
    return session.scalar(select(User).where(User.external_id == external_id))


COGNITO_ACCESS_TOKEN = {
    "sub": "cognito-sub-1",
    "cognito:groups": ["admins"],
    "client_id": "cognito-client",
    "origin_jti": "origin",
    "event_id": "event",
    "token_use": "access",
    "scope": "openid profile email",
    "auth_time": 1,
    "jti": "jti",
    "username": "bob",
}
KEYCLOAK_ACCESS_TOKEN = {
    "sub": "keycloak-sub-1",
    "aud": "portal",
    "azp": "portal",
    "typ": "Bearer",
    "scope": "openid profile email",
    "email_verified": True,
    "name": "Karel Token",
    "preferred_username": "karel",
    "given_name": "Karel",
    "family_name": "Token",
    "email": "karel@example.com",
}
ENTRA_AUDIENCE = "00001111-aaaa-2222-bbbb-3333cccc4444"
ENTRA_ACCESS_TOKEN = {
    "sub": "entra-pairwise-sub-1",
    "aud": ENTRA_AUDIENCE,
    "azp": "5555eeee-6666-ffff-7777-8888aaaa9999",
    "oid": "object-id-1",
    "tid": "tenant-id-1",
    "ver": "2.0",
    "scp": "access_as_user",
    "name": "Anna van Dijk",
    "preferred_username": "anna@contoso.com",
}


class TestAuthorizeUserIdentitySource:
    def test_get_authenticated_user__cognito_reads_identity_from_userinfo(
        self, idp, session
    ):
        idp(audience=None)
        bearer = sign(COGNITO_ACCESS_TOKEN)
        body = {
            "sub": "cognito-sub-1",
            "email_verified": "true",
            "email": "bob@example.com",
            "name": "Bob Builder",
            "given_name": "Bob",
            "family_name": "Builder",
            "username": "bob",
        }

        with userinfo_returns(200, body) as post:
            log_in(bearer, session)

        post.assert_called_once_with(
            url=USERINFO_URL, headers={"Authorization": bearer}
        )
        user = stored_user(session, "cognito-sub-1")
        assert (user.email, user.first_name, user.last_name) == (
            "bob@example.com",
            "Bob",
            "Builder",
        )

    @pytest.mark.parametrize(
        "outage",
        [
            pytest.param(
                {
                    "return_value": httpx.Response(
                        503, json={}, request=httpx.Request("POST", USERINFO_URL)
                    )
                },
                id="server-error",
            ),
            pytest.param(
                {"side_effect": httpx.ConnectTimeout("timed out")}, id="timeout"
            ),
        ],
    )
    def test_get_authenticated_user__userinfo_outage_returns_503_and_keeps_user(
        self, idp, session, outage
    ):
        idp(audience="portal")
        user = UserFactory(external_id="other-sub", email="karel.userinfo@example.com")
        bearer = sign(KEYCLOAK_ACCESS_TOKEN)

        with (
            patch("app.core.auth.auth.httpx.post", **outage),
            pytest.raises(HTTPException) as exc_info,
        ):
            log_in(bearer, session)

        assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert stored_user(session, "keycloak-sub-1") is None
        session.refresh(user)
        assert user.external_id == "other-sub"

    def test_get_authenticated_user__cognito_token_without_openid_scope_is_rejected(
        self, idp, session
    ):
        idp(audience=None)
        bearer = sign({**COGNITO_ACCESS_TOKEN, "scope": "portal/api"})

        with (
            userinfo_returns(401, {"error": "invalid_token"}),
            pytest.raises(HTTPException) as exc_info,
        ):
            log_in(bearer, session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert stored_user(session, "cognito-sub-1") is None

    def test_get_authenticated_user__keycloak_prefers_userinfo_over_token_claims(
        self, idp, session
    ):
        idp(audience="portal")
        bearer = sign(KEYCLOAK_ACCESS_TOKEN)
        body = {
            "sub": "keycloak-sub-1",
            "name": "Karel Userinfo",
            "given_name": "Karel",
            "family_name": "Userinfo",
            "email": "karel.userinfo@example.com",
            "preferred_username": "karel",
        }

        with userinfo_returns(200, body):
            log_in(bearer, session)

        user = stored_user(session, "keycloak-sub-1")
        assert (user.email, user.last_name) == (
            "karel.userinfo@example.com",
            "Userinfo",
        )

    def test_get_authenticated_user__keycloak_falls_back_when_userinfo_rejects_token(
        self, idp, session
    ):
        idp(audience="portal")
        bearer = sign(KEYCLOAK_ACCESS_TOKEN)

        with userinfo_returns(403, {"error": "insufficient_scope"}):
            log_in(bearer, session)

        user = stored_user(session, "keycloak-sub-1")
        assert (user.email, user.first_name, user.last_name) == (
            "karel@example.com",
            "Karel",
            "Token",
        )

    def test_get_authenticated_user__entra_reads_identity_from_token_claims(
        self, idp, session
    ):
        idp(audience=ENTRA_AUDIENCE)
        bearer = sign(ENTRA_ACCESS_TOKEN)

        with userinfo_returns(401, {"error": "InvalidAuthenticationToken"}) as post:
            log_in(bearer, session)

        post.assert_called_once()
        user = stored_user(session, "entra-pairwise-sub-1")
        assert (user.email, user.first_name, user.last_name) == (
            "anna@contoso.com",
            "Anna van",
            "Dijk",
        )

    def test_get_authenticated_user__entra_uses_optional_name_and_email_claims(
        self, idp, session
    ):
        idp(audience=ENTRA_AUDIENCE)
        bearer = sign(
            {
                **ENTRA_ACCESS_TOKEN,
                "given_name": "Anna",
                "family_name": "van Dijk",
                "email": "anna.vandijk@contoso.com",
            }
        )

        with userinfo_returns(401, {"error": "InvalidAuthenticationToken"}):
            log_in(bearer, session)

        user = stored_user(session, "entra-pairwise-sub-1")
        assert (user.email, user.first_name, user.last_name) == (
            "anna.vandijk@contoso.com",
            "Anna",
            "van Dijk",
        )

    def test_get_authenticated_user__entra_skips_preferred_username_without_at(
        self, idp, session
    ):
        idp(audience=ENTRA_AUDIENCE)
        bearer = sign(
            {
                **ENTRA_ACCESS_TOKEN,
                "preferred_username": "+3212345678",
                "upn": "anna@contoso.com",
            }
        )

        with userinfo_returns(401, {"error": "InvalidAuthenticationToken"}):
            log_in(bearer, session)

        assert stored_user(session, "entra-pairwise-sub-1").email == "anna@contoso.com"

    def test_get_authenticated_user__entra_without_email_claim_is_rejected(
        self, idp, session
    ):
        idp(audience=ENTRA_AUDIENCE)
        claims = {**ENTRA_ACCESS_TOKEN, "preferred_username": "anna"}
        bearer = sign(claims)

        with (
            userinfo_returns(401, {"error": "InvalidAuthenticationToken"}),
            pytest.raises(HTTPException) as exc_info,
        ):
            log_in(bearer, session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert stored_user(session, "entra-pairwise-sub-1") is None

    def test_get_authenticated_user__userinfo_html_response_falls_back_to_claims(
        self, idp, session
    ):
        idp(audience=ENTRA_AUDIENCE)
        bearer = sign(ENTRA_ACCESS_TOKEN)

        with userinfo_returns(200, "<html>login</html>"):
            log_in(bearer, session)

        assert stored_user(session, "entra-pairwise-sub-1").email == "anna@contoso.com"

    def test_get_authenticated_user__known_user_skips_userinfo(self, idp, session):
        idp(audience=ENTRA_AUDIENCE)
        UserFactory(external_id="entra-pairwise-sub-1", email="anna@contoso.com")
        bearer = sign(ENTRA_ACCESS_TOKEN)

        with userinfo_returns(200, {}) as post:
            user = log_in(bearer, session)

        post.assert_not_called()
        assert user.email == "anna@contoso.com"

    def test_get_authenticated_user__userinfo_email_links_new_subject(
        self, idp, session
    ):
        idp(audience="portal")
        existing = UserFactory(external_id="old-sub", email="karel@example.com")
        bearer = sign(KEYCLOAK_ACCESS_TOKEN)
        body = {**KEYCLOAK_ACCESS_TOKEN, "email": "karel@example.com"}

        with userinfo_returns(200, body):
            log_in(bearer, session)

        session.refresh(existing)
        assert existing.external_id == "keycloak-sub-1"

    def test_get_authenticated_user__token_claim_email_cannot_take_over_account(
        self, idp, session
    ):
        idp(audience=ENTRA_AUDIENCE)
        existing = UserFactory(external_id="admin-sub", email="anna@contoso.com")
        bearer = sign(ENTRA_ACCESS_TOKEN)

        with (
            userinfo_returns(401, {"error": "InvalidAuthenticationToken"}),
            pytest.raises(HTTPException) as exc_info,
        ):
            log_in(bearer, session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        session.refresh(existing)
        assert existing.external_id == "admin-sub"
        assert stored_user(session, "entra-pairwise-sub-1") is None

    @pytest.mark.parametrize(
        "bearer",
        [
            pytest.param(sign(ENTRA_ACCESS_TOKEN, expires_in=-60), id="expired"),
            pytest.param(sign({**ENTRA_ACCESS_TOKEN, "aud": "other"}), id="audience"),
            pytest.param(sign(ENTRA_ACCESS_TOKEN, key=OTHER_KEY), id="signature"),
            pytest.param("Bearer not-a-jwt", id="malformed"),
        ],
    )
    def test_secured_call__invalid_token_is_rejected_before_userinfo(
        self, idp, session, bearer
    ):
        idp(audience=ENTRA_AUDIENCE)

        with (
            userinfo_returns(200, {}) as post,
            pytest.raises(HTTPException) as exc_info,
        ):
            log_in(bearer, session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        post.assert_not_called()
        assert stored_user(session, "entra-pairwise-sub-1") is None

    def test_authorize_user__missing_access_token_is_rejected(self, idp, session):
        idp(audience=ENTRA_AUDIENCE)
        from app.core.auth.auth import authorize_user, secured_call

        with pytest.raises(HTTPException) as exc_info:
            authorize_user(token=secured_call(token=None), db=session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
