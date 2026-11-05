import os
from enum import Enum
from typing import Optional

import httpx
from fastapi.security import OpenIdConnect
from pydantic import BaseModel, model_validator

from app.core.config.env_var_parser import get_boolean_variable


class OIDCProvider(Enum):
    COGNITO = "cognito"


class OIDCConfiguration:
    def __init__(
        self,
        oidc_enabled: bool = False,
        provider: OIDCProvider = OIDCProvider.COGNITO,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        authority: Optional[str] = None,
        audience: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ):
        self.oidc_enabled = oidc_enabled or get_boolean_variable("OIDC_ENABLED", False)
        self.provider = provider

        if self.oidc_enabled:
            self.client_id = client_id or os.getenv("OIDC_CLIENT_ID")
            self.client_secret = client_secret or os.getenv("OIDC_CLIENT_SECRET")
            self.authority = authority or os.getenv("OIDC_AUTHORITY")
            self.audience = audience or os.getenv("OIDC_AUDIENCE")
            self.redirect_uri = redirect_uri or os.getenv("OIDC_REDIRECT_URI")
            if self.redirect_uri:
                self.redirect_uri = self.redirect_uri.removesuffix("/")

            configuration_url = f"{self.authority}/.well-known/openid-configuration"
            self.oidc_dependency = OpenIdConnect(
                openIdConnectUrl=configuration_url, auto_error=False
            )

            json_config = httpx.get(configuration_url).json()
            self.authorization_endpoint = json_config.get("authorization_endpoint")
            self.userinfo_endpoint = json_config.get("userinfo_endpoint")
            self.token_endpoint = json_config.get("token_endpoint")
            self.jwks_uri = json_config.get(
                "jwks_uri", f"{self.authority}/.well-known/jwks.json"
            )
            self.jwks_keys = httpx.get(url=self.jwks_uri).json()


class OIDCIdentity(BaseModel):
    sub: str
    name: str
    given_name: str
    family_name: str = ""
    email: str
    username: Optional[str] = None
    preferred_username: Optional[str] = None

    @model_validator(mode="before")
    def populate_username(cls, values):
        values["username"] = values.get("username") or values.get("preferred_username")
        values["given_name"] = values.get("given_name") or values.get("name")
        return values

    @classmethod
    def from_claims(cls, claims: dict) -> "OIDCIdentity":
        email = next(
            (
                value
                for value in (
                    claims.get("email"),
                    claims.get("preferred_username"),
                    claims.get("upn"),
                )
                if isinstance(value, str) and "@" in value
            ),
            None,
        )
        if not email:
            raise ValueError("token carries no email, preferred_username or upn claim")
        given_name = claims.get("given_name")
        family_name = claims.get("family_name") or ""
        if not given_name:
            display_name = claims.get("name") or email.split("@")[0]
            if family_name and display_name.endswith(f" {family_name}"):
                given_name = display_name.removesuffix(f" {family_name}")
            else:
                head, _, tail = display_name.rpartition(" ")
                given_name = head or tail
                family_name = family_name or (tail if head else "")
        return cls(
            sub=claims["sub"],
            name=claims.get("name") or given_name,
            given_name=given_name,
            family_name=family_name,
            email=email,
            preferred_username=claims.get("preferred_username"),
        )
