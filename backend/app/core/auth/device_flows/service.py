from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
from hashlib import sha256
from typing import Annotated
from uuid import uuid4

import httpx
import pytz
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth.device_flows.exceptions import (
    ExpiredDeviceCodeError,
    ExpiredUserCodeError,
    SlowDownException,
)
from app.core.auth.device_flows.model import DeviceFlow as DeviceFlowModel
from app.core.auth.device_flows.schema import (
    DeviceFlow,
    DeviceFlowStatus,
    OIDCTokenResponse,
)
from app.core.auth.jwt import get_oidc
from app.core.helpers.templates import render_html_template
from app.core.logging import logger
from app.settings import settings


def verify_auth_header(
    credentials: Annotated[HTTPBasicCredentials, Depends(HTTPBasic())],
) -> str:
    oidc = get_oidc()
    if not oidc.oidc_enabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="OIDC is not enabled"
        )

    if (
        credentials.username != oidc.client_id
        or credentials.password != oidc.client_secret
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "POST Call on /token invalid: "
                "authorization header does not match Cognito info"
            ),
        )
    return credentials.username


def utc_now() -> datetime:
    return datetime.now(tz=pytz.utc).replace(tzinfo=None)


class DeviceFlowService:
    def __init__(self):
        self.logger = logger

    @staticmethod
    def generate_device_flow_codes(
        db: Session, client_id: str, request: Request, scope: str = "openid"
    ) -> DeviceFlow:
        device_flow = DeviceFlowModel(
            client_id=client_id,
            scope=scope,
            max_expiry=utc_now()
            + timedelta(minutes=settings.DEVICE_CODE_FLOW_EXPIRY_MINUTES),
            oidc_redirect_uri=get_oidc().redirect_uri,
            last_checked=utc_now(),
        )
        db.add(device_flow)
        db.commit()

        base_url = request.url_for("device_flow_user_code")
        verification_uri = f"{base_url}?code={device_flow.user_code}"

        # Extract all ORM fields and add verification_uri_complete

        return DeviceFlow(
            **{k: v for k, v in device_flow.__dict__.items() if not k.startswith("_")},
            verification_uri_complete=verification_uri,
        )

    def fetch_jwt_tokens(
        self, request: Request, db: Session, device_code: str, client_id: str
    ) -> OIDCTokenResponse:
        self.logger.debug("requesting JWTs")
        device_flow = db.get(DeviceFlowModel, device_code)

        if not device_flow:
            raise ExpiredDeviceCodeError("Device code not found")
        if device_flow.status == "expired":
            raise ExpiredDeviceCodeError("The device code has already expired")
        if device_flow.client_id != client_id:
            raise ExpiredDeviceCodeError(
                "The client id does not match the initial requestor client id"
            )

        if utc_now() > device_flow.max_expiry:
            device_flow.status = DeviceFlowStatus.EXPIRED
            db.commit()
            raise ExpiredDeviceCodeError("The device code has expired")
        if utc_now() <= device_flow.last_checked + timedelta(
            seconds=device_flow.interval
        ):
            self.logger.debug(
                f"Client makes too much API calls {utc_now()},\
                {device_flow.last_checked}"
            )
            device_flow.last_checked = utc_now()
            db.commit()
            raise SlowDownException

        device_flow.last_checked = utc_now()
        self.logger.debug(
            f"Client is on time for checking, we got a status {device_flow.status}"
        )
        db.commit()
        if device_flow.status in (
            DeviceFlowStatus.AUTHORIZATION_PENDING,
            DeviceFlowStatus.DENIED,
        ) or (
            device_flow.status == DeviceFlowStatus.AUTHORIZED
            and not device_flow.authz_code
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=device_flow.status
            )
        elif (
            device_flow.status == DeviceFlowStatus.AUTHORIZED and device_flow.authz_code
        ):
            self.logger.debug("Launching Request for Tokens")

            oidc = get_oidc()
            response = httpx.post(
                oidc.token_endpoint,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": request.headers.get("Authorization"),
                },
                data={
                    "grant_type": "authorization_code",
                    "client_id": client_id,
                    "redirect_uri": f"{oidc.redirect_uri}"
                    f"{request.app.url_path_for('device_flow_callback')}",
                    "code": device_flow.authz_code,
                    "code_verifier": device_flow.authz_verif,
                },
            )

            response.raise_for_status()
            tokens = response.json()
            self.logger.debug(tokens)
            device_flow.status = DeviceFlowStatus.EXPIRED
            db.commit()
            return OIDCTokenResponse(**tokens)
        else:
            raise ExpiredDeviceCodeError

    @staticmethod
    def _verify_auth_header(auth_client_id: str, client_id: str) -> None:
        if auth_client_id != client_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=(
                    "POST Call on /token invalid: "
                    "client id in header does not match request"
                ),
            )

    def get_device_token(
        self,
        client_id: str,
        db: Session,
        request: Request,
        scope: str = "openid",
    ) -> DeviceFlow:
        return self.generate_device_flow_codes(db, client_id, request, scope)

    def get_jwt_token(
        self,
        request: Request,
        client_id: str,
        device_code: str,
        grant_type: str,
        db: Session,
    ) -> OIDCTokenResponse:
        if grant_type != "urn:ietf:params:oauth:grant-type:device_code":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="POST Call on /token invalid: incorrect grant type",
            )
        return self.fetch_jwt_tokens(request, db, device_code, client_id)

    def request_user_code_processing(
        self, user_code: str, request: Request, db: Session
    ) -> HTMLResponse:
        device_flows = db.scalars(
            select(DeviceFlowModel).where(DeviceFlowModel.user_code == user_code)
        ).all()

        if not device_flows or len(device_flows) != 1:
            raise ExpiredDeviceCodeError("Device code not found")
        device_flow = device_flows[0]
        if device_flow.status in (
            DeviceFlowStatus.EXPIRED,
            DeviceFlowStatus.AUTHORIZED,
            DeviceFlowStatus.DENIED,
        ):
            self.logger.debug("The device code has already been expired or been used")
            raise ExpiredUserCodeError
        if utc_now() > device_flow.max_expiry:
            self.logger.debug("User Code has expired")
            device_flow.status = DeviceFlowStatus.EXPIRED
            db.commit()
            raise ExpiredUserCodeError
        self.logger.debug("User Code is valid and action is authorize")
        # Generate URIs using url_for for base path, then add query params manually
        confirm_base = request.url_for("device_flow_allow")
        confirm_uri = (
            f"{confirm_base}?client_id={device_flow.client_id}"
            f"&device_code={device_flow.device_code}"
        )
        deny_base = request.url_for("device_flow_deny")
        deny_uri = (
            f"{deny_base}?client_id={device_flow.client_id}"
            f"&device_code={device_flow.device_code}"
        )
        return HTMLResponse(
            content=render_html_template(
                "device_confirm.html",
                {
                    "user_code": user_code,
                    "deny_uri": deny_uri,
                    "confirm_uri": confirm_uri,
                },
            )
        )

    @staticmethod
    def deny_device_flow(device_code: str, db: Session) -> RedirectResponse:
        device = db.get(DeviceFlowModel, device_code)
        device.status = DeviceFlowStatus.DENIED
        db.commit()
        return RedirectResponse("/")

    @staticmethod
    def allow_device_flow(
        client_id: str, device_code: str, db: Session, request: Request
    ) -> RedirectResponse:
        code_verifier = uuid4().hex
        digest = sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = urlsafe_b64encode(digest).decode("utf-8").replace("=", "")

        state = uuid4().hex

        device = db.get(DeviceFlowModel, device_code)
        device.authz_state = state
        device.authz_verif = code_verifier
        db.commit()

        oidc = get_oidc()
        callback_url = (
            f"{oidc.redirect_uri}{request.app.url_path_for('device_flow_callback')}"
        )

        return RedirectResponse(
            status_code=302,
            url=(
                f"{oidc.authorization_endpoint}?"
                f"response_type=code&client_id={client_id}"
                f"&scope={device.scope}&"
                f"redirect_uri={callback_url}"
                f"&state={state}&scope={device.scope}&code_challenge_method=S256"
                f"&code_challenge={code_challenge}"
                f"&identity_provider={oidc.provider.name}"
            ),
        )

    def process_authz_code_callback(
        self, authz_code: str, state: str, db: Session
    ) -> HTMLResponse:
        devices = db.scalars(
            select(DeviceFlowModel).where(DeviceFlowModel.authz_state == state)
        ).all()
        if len(devices) != 1:
            self.logger.debug("Not exactly one device flow found with this state")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="not exactly one device flow found with this state",
            )

        device = devices[0]
        device.authz_code = authz_code
        device.status = DeviceFlowStatus.AUTHORIZED
        db.commit()
        return HTMLResponse(content=render_html_template("device_authorized.html"))
