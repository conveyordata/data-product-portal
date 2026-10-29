import json
from typing import Any

import jwt
from jwt.algorithms import RSAAlgorithm
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from pydantic import BaseModel, Field

from app.core.auth.oidc import OIDCConfiguration
from app.core.logging import logger

oidc = OIDCConfiguration()


def get_oidc():
    return oidc


class JWTToken(BaseModel):
    sub: str
    token: str
    # Validated claims of the access token, empty for API-key and default-user tokens.
    claims: dict[str, Any] = Field(default_factory=dict)


class JWTTokenValid:
    def __init__(self, token: str):
        self.oidc = get_oidc()
        self.logger = logger
        self.token = token
        self.valid_jwt_token: dict[str, str] = {}

    def is_valid(self) -> bool:
        verifiable_token = bytes(self.token[len("Bearer ") :], encoding="utf-8")

        public_keys = {}
        for jwk in self.oidc.jwks_keys["keys"]:
            kid = jwk["kid"]
            public_keys[kid] = RSAAlgorithm.from_jwk(json.dumps(jwk))

        try:
            kid = jwt.get_unverified_header(verifiable_token)["kid"]
            self.valid_jwt_token = jwt.decode(
                jwt=verifiable_token,
                key=public_keys[kid],
                algorithms=["RS256"],
                issuer=self.oidc.authority,
                audience=self.oidc.audience,
            )
        except ExpiredSignatureError:
            self.logger.info("Access token rejected: expired")
            return False
        except PyJWTError as e:
            self.logger.warning(f"Access token rejected: {e}")
            return False
        except Exception as e:
            self.logger.warning(f"Access token rejected, unexpected error: {e!r}")
            return False
        return True
