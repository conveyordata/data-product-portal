from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import (
    Authorization,
    DataOutputDatasetAssociationResolver,
)
from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.data_outputs_datasets.service import DataOutputDatasetService
from app.database.database import get_db_session
from app.users.schema import User

router = APIRouter(
    prefix="/data_output_dataset_links", tags=["data_output_dataset_links"]
)


@router.post(
    "/approve/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                AuthorizationAction.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST,
                DataOutputDatasetAssociationResolver,
            )
        )
    ],
)
def approve_data_output_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return DataOutputDatasetService().approve_data_output_link(
        id, db, authenticated_user
    )


@router.post("/deny/{id}")
def deny_data_output_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return DataOutputDatasetService().deny_data_output_link(id, db, authenticated_user)


@router.post("/remove/{id}")
def remove_data_output_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return DataOutputDatasetService().remove_data_output_link(
        id, db, authenticated_user
    )


@router.get("/actions")
def get_user_pending_actions(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> list[DataOutputDatasetAssociation]:
    return DataOutputDatasetService().get_user_pending_actions(db, authenticated_user)
