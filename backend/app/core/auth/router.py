from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import authorize_user
from app.core.auth.credentials import AWSCredentials
from app.core.auth.device_flows.router import router as device
from app.core.auth.service import AuthService
from app.database.database import get_db_session
from app.dependencies import OnlyWithProductAccessName
from app.users.schema import User

router = APIRouter(prefix="/auth", tags=["auth"])
router.include_router(device)


@router.get("/user")
def authorize(
    authorized_user: User = Depends(authorize_user),
) -> User:
    return authorized_user


@router.get(
    "/aws_credentials",
    dependencies=[Depends(OnlyWithProductAccessName())],
)
def get_aws_credentials(
    data_product_name: str,
    environment: str,
    authorized_user: User = Depends(authorize_user),
    db: Session = Depends(get_db_session),
) -> AWSCredentials:
    return AuthService().get_aws_credentials(
        data_product_name, environment, authorized_user, db
    )
