from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.data_products_datasets.service import DataProductDatasetService
from app.database.database import get_db_session
from app.dependencies import only_dataproduct_dataset_link_owners
from app.users.schema import User

router = APIRouter(
    prefix="/data_product_dataset_links", tags=["data_product_dataset_links"]
)


@router.get("")
def get_all_requests(db: Session = Depends(get_db_session)):
    return DataProductDatasetService().get_all_requests(db)


@router.get("/status/{status}")
def get_requests_by_status(status: str, db: Session = Depends(get_db_session)):
    return DataProductDatasetService().get_requests_by_status(status, db)


@router.post(
    "/approve/{id}", dependencies=[Depends(only_dataproduct_dataset_link_owners)]
)
def approve_data_product_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return DataProductDatasetService().approve_data_product_link(
        id, db, authenticated_user
    )


@router.post("/deny/{id}", dependencies=[Depends(only_dataproduct_dataset_link_owners)])
def deny_data_product_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return DataProductDatasetService().deny_data_product_link(
        id, db, authenticated_user
    )


@router.post(
    "/remove/{id}", dependencies=[Depends(only_dataproduct_dataset_link_owners)]
)
def remove_data_product_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return DataProductDatasetService().remove_data_product_link(
        id, db, authenticated_user
    )


@router.get("/actions")
def get_user_pending_actions(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> list[DataProductDatasetAssociation]:
    return DataProductDatasetService().get_user_pending_actions(db, authenticated_user)
