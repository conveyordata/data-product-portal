from typing import Optional

import httpx
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth.api_key import secured_api_key
from app.core.auth.jwt import JWTToken, JWTTokenValid, PyJWTError, oidc
from app.core.auth.oidc import OIDCIdentity
from app.database.database import get_db_session
from app.settings import settings
from app.users.model import User as UserModel
from app.users.schema import User
from app.users.schema_request import UserCreate


def update_db_user(oidc_user: OIDCIdentity, token: JWTToken, db: Session) -> User:
    db_user = db.scalar(select(UserModel).where(UserModel.external_id == token.sub))
    if db_user:
        db_user.email = oidc_user.email
        db_user.first_name = oidc_user.name
        db_user.last_name = oidc_user.family_name
    else:
        db_user = db.scalar(select(UserModel).where(UserModel.email == oidc_user.email))
        if db_user:
            db_user.external_id = oidc_user.sub
            db_user.first_name = oidc_user.name
            db_user.last_name = oidc_user.family_name
        else:
            created_user = UserCreate(
                email=oidc_user.email,
                external_id=oidc_user.sub,
                first_name=oidc_user.name,
                last_name=oidc_user.family_name,
            )
            db_user = UserModel(**created_user.model_dump())
            db.add(db_user)

    db.commit()

    User.model_validate(db_user)
    return db_user


if settings.OIDC_ENABLED:

    def unvalidated_token(token: str = Depends(oidc.oidc_dependency)) -> str:
        return token

    def secured_call(token: str = Depends(oidc.oidc_dependency)) -> JWTToken:
        jwt = JWTTokenValid(token)
        if not jwt.is_valid():
            raise PyJWTError()
        return JWTToken(sub=jwt.valid_jwt_token.get("sub"), token=token)

    def authorize_user(
        token: JWTToken = Depends(secured_call), db: Session = Depends(get_db_session)
    ) -> User:
        response = httpx.post(
            url=oidc.userinfo_endpoint, headers={"Authorization": token.token}
        )
        oidc_user = OIDCIdentity.model_validate(response.json())
        return update_db_user(oidc_user, token, db)

    def api_key_authenticated(
        api_key=Depends(secured_api_key), jwt_token=Depends(unvalidated_token)
    ):
        if not (api_key or jwt_token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Unauthenticated"
            )
        if not api_key:
            return secured_call(jwt_token)
        else:
            return JWTToken(sub="systemaccount_bot", token="")

    def get_authenticated_user(
        token: JWTToken = Depends(api_key_authenticated),
        db: Session = Depends(get_db_session),
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

    def authorize_user(
        db: Session = Depends(get_db_session)
    ) -> User:
        default_username = settings.DEFAULT_USERNAME
        if '@' not in default_username:
            raise Exception("Default username must be an email address")
        oidc_user = OIDCIdentity(
            sub=default_username,
            name=default_username.split(".")[0],
            family_name=default_username.split("@")[0].split(".")[1],
            email=default_username,
            username=default_username,
        )
        token = generate_default_jwt_token()
        return update_db_user(oidc_user, token, db)


    def generate_default_jwt_token(default_username = settings.DEFAULT_USERNAME):
        token = JWTToken(sub=default_username, token="token_value")
        return token


    def get_authenticated_user(
        db: Session = Depends(get_db_session)
    ) -> User:
        token = generate_default_jwt_token()
        user: Optional[User] = db.scalars(
            select(UserModel).where(UserModel.external_id == token.sub)
        ).one_or_none()
        if not user:
            return authorize_user(token, db)
        return user

    def api_key_authenticated(
        jwt_token=Depends(unvalidated_token)
    ):
        return secured_call(jwt_token)
