import os
from enum import Enum
from typing import Optional

import httpx
from fastapi.security import OpenIdConnect
from pydantic import BaseModel

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
        redirect_uri: Optional[str] = None,
    ):
        if oidc_enabled or get_boolean_variable("OIDC_ENABLED", False):
            self.client_id = client_id if client_id else os.getenv("OIDC_CLIENT_ID")
            self.client_secret = (
                client_secret if client_secret else os.getenv("OIDC_CLIENT_SECRET")
            )
            self.authority = authority if authority else os.getenv("OIDC_AUTHORITY")
            self.redirect_uri = (
                redirect_uri if redirect_uri else os.getenv("OIDC_REDIRECT_URI")
            )
            self.oidc_enabled = oidc_enabled
            self.provider = provider
            self.configuration_url = (
                f"{self.authority}/.well-known/openid-configuration"
            )
            json_config = httpx.get(self.configuration_url).json()
            self.authorization_endpoint = json_config.get("authorization_endpoint")
            self.userinfo_endpoint = json_config.get("userinfo_endpoint")
            self.token_endpoint = json_config.get("token_endpoint")
            if json_config.get("jwks_uri"):
                self.jwks_keys = httpx.get(url=json_config.get("jwks_uri")).json()
            else:
                self.jwks_keys = httpx.get(
                    url=f"{self.authority}/.well-known/jwks.json"
                ).json()
            self.oidc_dependency = OpenIdConnect(
                openIdConnectUrl=self.configuration_url, auto_error=False
            )


class OIDCIdentity(BaseModel):
    sub: str
    name: str
    family_name: str
    email: str
    username: str
