from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.auth.device_flows.schema import DeviceFlow, OIDCTokenResponse
from app.core.auth.device_flows.service import DeviceFlowService, verify_auth_header
from app.database.database import get_db_session

router = APIRouter(prefix="/device")


@router.post("/device_token")
async def get_device_token(
    request: Request,
    auth_client_id: Annotated[str, Depends(verify_auth_header)],
    client_id: str = Query(default="", deprecated=True),
    scope: str = "openid",
    db: Session = Depends(get_db_session),
) -> DeviceFlow:
    return DeviceFlowService().get_device_token(auth_client_id, db, request, scope)


@router.post("/jwt_token")
async def get_jwt_token(
    request: Request,
    device_code: str,
    grant_type: str,
    auth_client_id: Annotated[str, Depends(verify_auth_header)],
    client_id: str = Query(default="", deprecated=True),
    db: Session = Depends(get_db_session),
) -> OIDCTokenResponse:
    return DeviceFlowService().get_jwt_token(
        request, auth_client_id, device_code, grant_type, db
    )


@router.get("", include_in_schema=False, name="device_flow_user_code")
async def request_user_code_processing(
    code: str, request: Request, db: Session = Depends(get_db_session)
) -> HTMLResponse:
    return DeviceFlowService().request_user_code_processing(code, request, db)


@router.get("/deny", include_in_schema=False, name="device_flow_deny")
def deny_device_flow(
    device_code: str, db: Session = Depends(get_db_session)
) -> RedirectResponse:
    return DeviceFlowService().deny_device_flow(device_code, db)


@router.get("/allow", include_in_schema=False, name="device_flow_allow")
def allow_device_flow(
    client_id: str,
    device_code: str,
    request: Request,
    db: Session = Depends(get_db_session),
) -> RedirectResponse:
    return DeviceFlowService().allow_device_flow(client_id, device_code, db, request)


@router.get("/callback", include_in_schema=False, name="device_flow_callback")
def process_authz_code_callback(
    code: str, state: str, db: Session = Depends(get_db_session)
) -> HTMLResponse:
    return DeviceFlowService().process_authz_code_callback(code, state, db)
