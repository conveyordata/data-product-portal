from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, DataProductDatasetAssociationResolver
from app.data_products_datasets.service import DataProductDatasetService
from app.database.database import get_db_session
from app.pending_actions.schema import DataProductDatasetPendingAction
from app.users.schema import User

router = APIRouter(
    prefix="/data_product_dataset_links", tags=["data_product_dataset_links"]
)


@router.post(
    "/approve/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATASET__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                DataProductDatasetAssociationResolver,
            )
        ),
    ],
)
def approve_data_product_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return DataProductDatasetService().approve_data_product_link(
        id, db, authenticated_user
    )


@router.post(
    "/deny/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATASET__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                DataProductDatasetAssociationResolver,
            )
        ),
    ],
)
def deny_data_product_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    return DataProductDatasetService().deny_data_product_link(
        id, db, authenticated_user
    )


@router.post(
    "/remove/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATASET__REVOKE_DATAPRODUCT_ACCESS,
                DataProductDatasetAssociationResolver,
            )
        ),
    ],
)
def remove_data_product_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    return DataProductDatasetService().remove_data_product_link(
        id, db, authenticated_user
    )


@router.get("/actions")
def get_user_pending_actions(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> Sequence[DataProductDatasetPendingAction]:
    return DataProductDatasetService().get_user_pending_actions(db, authenticated_user)
