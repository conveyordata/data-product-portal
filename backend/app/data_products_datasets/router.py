from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.data_products_datasets.service import DataProductDatasetService
from app.database.database import get_db_session
from app.dependencies import only_dataproduct_dataset_link_owners
from app.users.schema import User

router = APIRouter(
    prefix="/data_product_dataset_links", tags=["data_product_dataset_links"]
)


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
