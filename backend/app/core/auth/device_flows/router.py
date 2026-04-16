from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.auth.device_flows.service import DeviceFlowService, verify_auth_header
from app.database.database import get_db_session

router = APIRouter(prefix="/device")


@router.post("/device_token")
async def get_device_token(
    request: Request,
    client_id: str,
    auth_client_id: Annotated[str, Depends(verify_auth_header)],
    scope: str = "openid",
    db: Session = Depends(get_db_session),
):
    return DeviceFlowService().get_device_token(
        auth_client_id, client_id, db, request, scope
    )


@router.post("/jwt_token")
async def get_jwt_token(
    request: Request,
    client_id: str,
    device_code: str,
    grant_type: str,
    auth_client_id: Annotated[str, Depends(verify_auth_header)],
    db: Session = Depends(get_db_session),
):
    return DeviceFlowService().get_jwt_token(
        request, auth_client_id, client_id, device_code, grant_type, db
    )


@router.get("", include_in_schema=False, name="device_flow_user_code")
async def request_user_code_processing(
    code: str, request: Request, db: Session = Depends(get_db_session)
):
    return DeviceFlowService().request_user_code_processing(code, request, db)


@router.get("/deny", include_in_schema=False, name="device_flow_deny")
def deny_device_flow(device_code: str, db: Session = Depends(get_db_session)):
    return DeviceFlowService().deny_device_flow(device_code, db)


@router.get("/allow", include_in_schema=False, name="device_flow_allow")
def allow_device_flow(
    client_id: str,
    device_code: str,
    request: Request,
    db: Session = Depends(get_db_session),
):
    return DeviceFlowService().allow_device_flow(client_id, device_code, db, request)


@router.get("/callback", include_in_schema=False, name="device_flow_callback")
def process_authz_code_callback(
    code: str, state: str, db: Session = Depends(get_db_session)
):
    return DeviceFlowService().process_authz_code_callback(code, state, db)
