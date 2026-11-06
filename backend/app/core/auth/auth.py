from typing import Annotated, Optional

import httpx
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth.api_key import secured_api_key
from app.core.auth.jwt import JWTToken, JWTTokenValid
from app.core.auth.oidc import OIDCIdentity
from app.core.logging import logger
from app.database.database import get_system_db_session
from app.settings import settings
from app.users.model import User as UserModel
from app.users.schema import User
from app.users.schema_request import UserCreate

SYSTEM_ACCOUNT_BOT_EXTERNAL_ID = "systemaccount_bot"


def update_db_user(
    oidc_user: OIDCIdentity, token: JWTToken, db: Session, link_by_email: bool = True
) -> User:
    db_user = db.scalar(select(UserModel).where(UserModel.external_id == token.sub))
    email_owner = db.scalar(select(UserModel).where(UserModel.email == oidc_user.email))
    if email_owner and email_owner is not db_user and (db_user or not link_by_email):
        logger.warning("Identity email belongs to a user with another subject")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This email belongs to another account",
        )
    if db_user:
        db_user.email = oidc_user.email
        db_user.first_name = oidc_user.given_name
        db_user.last_name = oidc_user.family_name
    elif email_owner:
        db_user = email_owner
        db_user.external_id = token.sub
        db_user.first_name = oidc_user.given_name
        db_user.last_name = oidc_user.family_name
    else:
        created_user = UserCreate(
            email=oidc_user.email,
            external_id=token.sub,
            first_name=oidc_user.given_name,
            last_name=oidc_user.family_name,
        )
        db_user = UserModel(**created_user.model_dump())
        db.add(db_user)

    db.commit()

    User.model_validate(db_user)
    return db_user


if settings.OIDC_ENABLED:
    from app.core.auth.jwt import oidc

    def unvalidated_token(token: str = Depends(oidc.oidc_dependency)) -> str:
        return token

    def secured_call(token: str = Depends(oidc.oidc_dependency)) -> JWTToken:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing access token",
            )
        jwt = JWTTokenValid(token)
        if not jwt.is_valid():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token",
            )
        sub = jwt.valid_jwt_token.get(settings.OIDC_USER_ID_CLAIM)
        if not sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token lacks the user id claim",
            )
        return JWTToken(sub=sub, token=token, claims=jwt.valid_jwt_token)

    def authorize_user(
        token: JWTToken = Depends(secured_call),
        db: Session = Depends(get_system_db_session),
    ) -> User:
        if settings.OIDC_IDENTITY_SOURCE == "access_token":
            oidc_user = _identity_from_claims(token)
            return update_db_user(
                oidc_user,
                token,
                db,
                link_by_email=_email_verified(token.claims, oidc_user.email),
            )
        return update_db_user(_identity_from_userinfo(token), token, db)

    def _identity_from_userinfo(token: JWTToken) -> OIDCIdentity:
        try:
            response = httpx.post(
                url=oidc.userinfo_endpoint, headers={"Authorization": token.token}
            )
        except httpx.HTTPError as e:
            logger.warning(f"Userinfo unreachable: {type(e).__name__}")
            raise _identity_provider_unavailable()
        if response.is_server_error:
            logger.warning(f"Userinfo failed with status {response.status_code}")
            raise _identity_provider_unavailable()
        if response.is_client_error:
            logger.warning(
                f"Userinfo rejected the access token: {response.status_code}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Userinfo rejected the access token",
            )
        try:
            return OIDCIdentity.model_validate(response.json())
        except ValueError as e:
            logger.warning(f"Userinfo returned no usable identity: {type(e).__name__}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Userinfo returned no usable identity",
            )

    def _identity_from_claims(token: JWTToken) -> OIDCIdentity:
        try:
            return OIDCIdentity.from_claims(
                token.claims, token.sub, settings.OIDC_EMAIL_CLAIM
            )
        except (KeyError, ValueError) as e:
            logger.warning(f"Access token lacks identity claims: {type(e).__name__}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token lacks identity claims",
            )

    def _email_verified(claims: dict, email: str) -> bool:
        verified = claims.get("email_verified")
        return claims.get("email") == email and (verified is True or verified == "true")

    def _identity_provider_unavailable() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Identity provider unavailable",
        )

    def api_key_authenticated(
        api_key=Depends(secured_api_key), jwt_token=Depends(unvalidated_token)
    ) -> JWTToken:
        if not api_key and not jwt_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Unauthenticated"
            )
        if not api_key:
            return secured_call(jwt_token)
        else:
            return JWTToken(sub=SYSTEM_ACCOUNT_BOT_EXTERNAL_ID, token="")

    def get_authenticated_user(
        token: JWTToken = Depends(api_key_authenticated),
        db: Session = Depends(get_system_db_session, scope="function"),
    ) -> User:
        result = db.scalars(
            select(UserModel).where(UserModel.external_id == token.sub)
        ).one_or_none()
        if not result:
            return authorize_user(token, db)
        return result

else:

    def unvalidated_token(token: str = "") -> str:
        return token

    def user(
        user: Annotated[
            Optional[str], Header(alias="X-User", include_in_schema=False)
        ] = None,
    ) -> str:
        if user:
            return user
        return settings.DEFAULT_USERNAME

    # The token dependency is replaced by the user we want to use in this mode
    def secured_call(
        token: str = Depends(user),
    ) -> JWTToken:
        return generate_default_jwt_token(user=token)

    def generate_default_jwt_token(
        user: str,
    ) -> JWTToken:
        return JWTToken(sub=user, token="")

    def authorize_user(
        token: JWTToken = Depends(secured_call),
        db: Session = Depends(get_system_db_session, scope="function"),
    ) -> User:
        if "@" not in token.sub:
            raise Exception("Default username must be an email address")
        name, _, family_name = token.sub.split("@")[0].partition(".")
        oidc_user = OIDCIdentity(
            sub=token.sub,
            name=name,
            family_name=family_name,
            email=token.sub,
            username=token.sub,
        )
        return update_db_user(oidc_user, token, db)

    def get_authenticated_user(
        token: JWTToken = Depends(secured_call),
        db: Session = Depends(get_system_db_session, scope="function"),
    ) -> User:
        user: Optional[User] = db.scalars(
            select(UserModel).where(UserModel.external_id == token.sub)
        ).one_or_none()
        if not user:
            return authorize_user(token, db)
        return user

    def api_key_authenticated(
        api_key=Depends(secured_api_key), jwt_token=Depends(unvalidated_token)
    ) -> JWTToken:
        return secured_call(jwt_token)
