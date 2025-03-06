import json

import jwt
from jwt.algorithms import RSAAlgorithm
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from pydantic import BaseModel

from app.core.auth.oidc import OIDCConfiguration
from app.core.logging.logger import logger

oidc = OIDCConfiguration()


def get_oidc():
    return oidc


class JWTToken(BaseModel):
    sub: str
    token: str


class JWTTokenValid:
    def __init__(self, token: str):
        self.oidc = oidc
        self.logger = logger
        self.token = token
        self.valid_jwt_token: dict[str, str] = {}

    def is_valid(self) -> bool:
        verifiable_token = bytes(self.token[len("Bearer ") :], encoding="utf-8")

        public_keys = {}
        for jwk in self.oidc.jwks_keys["keys"]:
            kid = jwk["kid"]
            public_keys[kid] = RSAAlgorithm.from_jwk(json.dumps(jwk))

        kid = jwt.get_unverified_header(verifiable_token)["kid"]
        try:
            self.valid_jwt_token = jwt.decode(
                jwt=verifiable_token,
                key=public_keys[kid],
                algorithms=["RS256"],
                issuer=self.oidc.authority,
            )
        except ExpiredSignatureError as e:
            self.logger.debug("jwt token is expired", e)
            return False
        except PyJWTError as e:
            self.logger.debug("Problem parsing jwt token", e)
            return False
        except Exception as e:
            self.logger.debug("Generic exception: Problem parsing jwt token", e)
            return False
        return True
