from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.data_product_memberships.enums import DataProductUserRole
from app.data_products.schema import (
    DataProductAboutUpdate,
    DataProductCreate,
    DataProductUpdate,
)
from app.data_products.schema_get import DataProductGet, DataProductsGet
from app.data_products.service import DataProductService
from app.database.database import get_db_session
from app.dependencies import OnlyProductRoles
from app.users.schema import User

router = APIRouter(prefix="/data_products", tags=["data_products"])


@router.get("")
def get_data_products(db: Session = Depends(get_db_session)) -> list[DataProductsGet]:
    return DataProductService().get_data_products(db)


@router.get("/user/{user_id}")
def get_user_data_products(
    user_id: UUID, db: Session = Depends(get_db_session)
) -> list[DataProductsGet]:
    return DataProductService().get_user_data_products(user_id, db)


@router.get("/{id}")
def get_data_product(id: UUID, db: Session = Depends(get_db_session)) -> DataProductGet:
    return DataProductService().get_data_product(id, db)


@router.post(
    "",
    responses={
        200: {
            "description": "Data Product successfully created",
            "content": {
                "application/json": {
                    "example": {"id": "random id of the new data_product"}
                }
            },
        },
        404: {
            "description": "Owner not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User id for owner not found"}
                }
            },
        },
    },
)
def create_data_product(
    data_product: DataProductCreate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> dict[str, UUID]:
    return DataProductService().create_data_product(
        data_product, db, authenticated_user
    )


@router.delete(
    "/{id}",
    responses={
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        }
    },
    dependencies=[Depends(OnlyProductRoles([DataProductUserRole.OWNER]))],
)
def remove_data_product(id: UUID, db: Session = Depends(get_db_session)):
    return DataProductService().remove_data_product(id, db)


@router.put(
    "/{id}",
    responses={
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        }
    },
    dependencies=[Depends(OnlyProductRoles([DataProductUserRole.MEMBER]))],
)
def update_data_product(
    id: UUID, data_product: DataProductUpdate, db: Session = Depends(get_db_session)
):
    return DataProductService().update_data_product(id, data_product, db)


@router.put(
    "/{id}/about",
    responses={
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        }
    },
    dependencies=[Depends(OnlyProductRoles([DataProductUserRole.MEMBER]))],
)
def update_data_product_about(
    id: UUID,
    data_product: DataProductAboutUpdate,
    db: Session = Depends(get_db_session),
):
    return DataProductService().update_data_product_about(id, data_product, db)


@router.post(
    "/{id}/dataset/{dataset_id}",
    responses={
        400: {
            "description": "Dataset not found",
            "content": {
                "application/json": {"example": {"detail": "Dataset not found"}}
            },
        },
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        },
    },
    dependencies=[Depends(OnlyProductRoles([DataProductUserRole.OWNER]))],
)
def link_dataset_to_data_product(
    id: UUID,
    dataset_id: UUID,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
):
    return DataProductService().link_dataset_to_data_product(
        id, dataset_id, authenticated_user, db
    )


@router.delete(
    "/{id}/dataset/{dataset_id}",
    responses={
        400: {
            "description": "Dataset not found",
            "content": {
                "application/json": {"example": {"detail": "Dataset not found"}}
            },
        },
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        },
    },
    dependencies=[Depends(OnlyProductRoles([DataProductUserRole.OWNER]))],
)
def unlink_dataset_from_data_product(
    id: UUID,
    dataset_id: UUID,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
):
    return DataProductService().unlink_dataset_from_data_product(
        id, dataset_id, authenticated_user, db
    )


@router.get(
    "/{id}/role", dependencies=[Depends(OnlyProductRoles([DataProductUserRole.MEMBER]))]
)
def get_role(id: UUID, environment: str, db: Session = Depends(get_db_session)) -> str:
    return DataProductService().get_data_product_role_arn(id, environment, db)


@router.get(
    "/{id}/signin_url",
    dependencies=[Depends(OnlyProductRoles([DataProductUserRole.MEMBER]))],
)
def get_signin_url(
    id: UUID,
    environment: str,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> str:
    return DataProductService().generate_signin_url(
        id, environment, authenticated_user, db
    )


@router.get(
    "/{id}/conveyor_notebook_url",
    dependencies=[Depends(OnlyProductRoles([DataProductUserRole.MEMBER]))],
)
def get_conveyor_notebook_url(id: UUID, db: Session = Depends(get_db_session)) -> str:
    return DataProductService().get_conveyor_notebook_url(id, db)


@router.get(
    "/{id}/conveyor_ide_url",
    dependencies=[Depends(OnlyProductRoles([DataProductUserRole.MEMBER]))],
)
def get_conveyor_ide_url(id: UUID, db: Session = Depends(get_db_session)) -> str:
    return DataProductService().get_conveyor_ide_url(id, db)
