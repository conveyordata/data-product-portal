from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import (
    Action,
    Authorization,
    DataProductResolver,
)
from app.data_product_memberships.schema_get import DataProductMembershipGet
from app.data_product_memberships.service import DataProductMembershipService
from app.database.database import get_db_session
from app.users.schema import User

router = APIRouter(
    prefix="/data_product_memberships", tags=["data_product_memberships"]
)


@router.post(
    "/request",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__REQUEST_DATAPRODUCT_ACCESS,
                DataProductResolver,
                object_id="data_product_id",
            )
        )
    ],
)
def request_data_product_membership(
    user_id: UUID,
    data_product_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return DataProductMembershipService().request_user_access_to_data_product(
        user_id, data_product_id, authenticated_user, db, background_tasks
    )


@router.get("/actions")
def get_user_pending_actions(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> list[DataProductMembershipGet]:
    return DataProductMembershipService().get_user_pending_actions(
        db, authenticated_user
    )
