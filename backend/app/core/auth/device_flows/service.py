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
from app.core.auth.device_flows.schema import DeviceFlow, DeviceFlowStatus
from app.core.auth.jwt import get_oidc
from app.core.helpers.templates import render_html_template
from app.core.logging import logger

basic_auth = HTTPBasic()


def verify_auth_header(
    credentials: Annotated[HTTPBasicCredentials, Depends(basic_auth)],
) -> bool:
    if (
        credentials.username != get_oidc().client_id
        or credentials.password != get_oidc().client_secret
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

    def generate_device_flow_codes(
        self, db: Session, client_id: str, scope: str = "openid"
    ) -> DeviceFlow:
        device_flow = DeviceFlowModel(
            client_id=client_id,
            scope=scope,
            max_expiry=utc_now() + timedelta(seconds=1800),
            oidc_redirect_uri=get_oidc().redirect_uri,
        )
        db.add(device_flow)
        db.commit()
        return DeviceFlow.model_validate(device_flow)

    def fetch_jwt_tokens(
        self, request: Request, db: Session, device_code: str, client_id: str
    ):
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
            raise SlowDownException()

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
            # This should not really be a 400 bad request?
            # Or maybe it should? This is thrown when the user has not yet authorized.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=device_flow.status
            )
        elif (
            device_flow.status == DeviceFlowStatus.AUTHORIZED and device_flow.authz_code
        ):
            self.logger.debug("Launching Request for Tokens")

            response = httpx.post(
                get_oidc().token_endpoint,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": request.headers.get("Authorization"),
                },
                data={
                    "grant_type": "authorization_code",
                    "client_id": client_id,
                    "redirect_uri": f"{get_oidc().redirect_uri}"
                    "api/auth/device/callback/",
                    "code": device_flow.authz_code,
                    "code_verifier": device_flow.authz_verif,
                },
            )

            data = response.json()
            self.logger.debug(data)
            device_flow.status = DeviceFlowStatus.EXPIRED
            db.commit()
            return data
        else:
            raise ExpiredDeviceCodeError()

    def _verify_auth_header(self, auth_client_id: str, client_id: str) -> bool:
        if auth_client_id != client_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=(
                    "POST Call on /token invalid: "
                    "client id in header does not match request"
                ),
            )
        return True

    def get_device_token(
        self, auth_client_id: str, client_id: str, db: Session, scope: str = "openid"
    ) -> DeviceFlow:
        assert self._verify_auth_header(auth_client_id, client_id)
        return self.generate_device_flow_codes(db, client_id, scope)

    def get_jwt_token(
        self,
        request: Request,
        auth_client_id: str,
        client_id: str,
        device_code: str,
        grant_type: str,
        db: Session,
    ):
        if grant_type != "urn:ietf:params:oauth:grant-type:device_code":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="POST Call on /token invalid: incorrect grant type",
            )
        assert self._verify_auth_header(auth_client_id, client_id)
        return self.fetch_jwt_tokens(request, db, device_code, client_id)

    def request_user_code_processing(
        self, user_code: str, request: Request, db: Session
    ):
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
            raise ExpiredUserCodeError()
        if utc_now() > device_flow.max_expiry:
            self.logger.debug("User Code has expired")
            device_flow.status = DeviceFlowStatus.EXPIRED
            db.commit()
            raise ExpiredUserCodeError()
        self.logger.debug("User Code is valid and action is authorize")
        confirm_uri = (
            "/api/auth/device/allow?"
            f"client_id={device_flow.client_id}&device_code={device_flow.device_code}"
        )
        deny_uri = (
            "/api/auth/device/deny?client_id"
            f"={device_flow.client_id}&device_code={device_flow.device_code}"
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

    def deny_device_flow(self, device_code: str, db: Session):
        device = db.get(DeviceFlowModel, device_code)
        device.status = DeviceFlowStatus.DENIED
        db.commit()
        return RedirectResponse("/")

    def allow_device_flow(self, client_id: str, device_code: str, db: Session):
        code_verifier = uuid4().hex
        hash = sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = urlsafe_b64encode(hash).decode("utf-8").replace("=", "")

        state = uuid4().hex

        device = db.get(DeviceFlowModel, device_code)
        device.authz_state = state
        device.authz_verif = code_verifier
        db.commit()

        return RedirectResponse(
            status_code=302,
            url=(
                f"{get_oidc().authorization_endpoint}?"
                f"response_type=code&client_id={client_id}"
                f"&scope={device.scope}&"
                f"redirect_uri={get_oidc().redirect_uri}api/auth/device/callback/"
                f"&state={state}&scope={device.scope}&code_challenge_method=S256"
                f"&code_challenge={code_challenge}"
                f"&identity_provider={get_oidc().provider.name}"
            ),
        )

    def process_authz_code_callback(self, authz_code: str, state: str, db: Session):
        devices = db.scalars(
            select(DeviceFlowModel).where(DeviceFlowModel.authz_state == state)
        ).all()
        if len(devices) != 1:
            self.logger.debug("Not exactly one device flow found with this state")
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="not exactly one device flow found with this state",
            )

        device = devices[0]
        device.authz_code = authz_code
        device.status = DeviceFlowStatus.AUTHORIZED
        db.commit()
        return HTMLResponse(content=render_html_template("device_authorized.html"))
