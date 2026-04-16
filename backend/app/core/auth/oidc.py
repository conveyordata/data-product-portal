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
        if oidc_enabled or get_boolean_variable("OIDC_ENABLED", False):
            self.client_id = client_id or os.getenv("OIDC_CLIENT_ID")
            self.client_secret = client_secret or os.getenv("OIDC_CLIENT_SECRET")
            self.authority = authority or os.getenv("OIDC_AUTHORITY")
            self.audience = audience or os.getenv("OIDC_AUDIENCE")
            self.redirect_uri = redirect_uri or os.getenv("OIDC_REDIRECT_URI")
            if self.redirect_uri:
                self.redirect_uri = self.redirect_uri.removesuffix("/")
            self.oidc_enabled = oidc_enabled
            self.provider = provider
            self.configuration_url = (
                f"{self.authority}/.well-known/openid-configuration"
            )
            json_config = httpx.get(self.configuration_url).json()
            self.authorization_endpoint = json_config.get("authorization_endpoint")
            self.userinfo_endpoint = json_config.get("userinfo_endpoint")
            self.token_endpoint = json_config.get("token_endpoint")
            self.jwks_uri = json_config.get(
                "jwks_uri", f"{self.authority}/.well-known/jwks.json"
            )
            self.jwks_keys = httpx.get(url=self.jwks_uri).json()
            self.oidc_dependency = OpenIdConnect(
                openIdConnectUrl=self.configuration_url, auto_error=False
            )


class OIDCIdentity(BaseModel):
    sub: str
    name: str
    family_name: str
    email: str
    username: Optional[str] = None
    preferred_username: Optional[str] = None

    @model_validator(mode="before")
    def populate_username(cls, values):
        values["username"] = values.get("username") or values.get("preferred_username")
        return values
