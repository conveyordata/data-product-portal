from app.core.auth.oidc import OIDCConfiguration
from jose import jwt
from logging import getLogger
from jose.exceptions import JWTClaimsError, JWTError, ExpiredSignatureError
from pydantic import BaseModel

oidc = OIDCConfiguration()


class JWTToken(BaseModel):
    sub: str
    token: str


class JWTTokenValid:
    def __init__(self, token: str):
        self.oidc = oidc
        self.logger = getLogger()
        self.token = token
        self.valid_jwt_token: dict[str, str] = {}

    def is_valid(self) -> bool:
        verifyable_token = bytes(self.token[len("Bearer ") :], encoding="utf-8")

        # get the algorithm type from the request header
        algorithm = jwt.get_unverified_header(verifyable_token).get("alg")

        try:
            self.valid_jwt_token = jwt.decode(
                token=verifyable_token,
                key=self.oidc.jwks_keys,
                algorithms=algorithm,
                issuer=self.oidc.authority,
            )
        except JWTClaimsError as e:
            self.logger.debug("Invalid claims in jwt token", e)
            return False
        except ExpiredSignatureError as e:
            self.logger.debug("jwt token is expired", e)
            return False
        except JWTError as e:
            self.logger.debug("Problem parsing jwt token", e)
            return False
        return True
