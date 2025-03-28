from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization, DataProductResolver
from app.data_outputs.schema import DataOutputCreateRequest
from app.data_outputs.schema_get import DataOutputGet
from app.data_outputs.service import DataOutputService
from app.data_product_memberships.enums import DataProductUserRole
from app.data_product_settings.service import DataProductSettingService
from app.data_products.schema import (
    DataProductAboutUpdate,
    DataProductCreate,
    DataProductStatusUpdate,
    DataProductUpdate,
)
from app.data_products.schema_get import DataProductGet, DataProductsGet
from app.data_products.service import DataProductService
from app.database.database import get_db_session
from app.dependencies import OnlyWithProductAccessID
from app.graph.graph import Graph
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
    dependencies=[
        Depends(OnlyWithProductAccessID([DataProductUserRole.OWNER])),
        Depends(
            Authorization.enforce(
                AuthorizationAction.DATA_PRODUCT__DELETE, DataProductResolver
            )
        ),
    ],
)
def remove_data_product(
    id: UUID,
    db: Session = Depends(get_db_session),
):
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
    dependencies=[Depends(OnlyWithProductAccessID())],
)
def update_data_product(
    id: UUID, data_product: DataProductUpdate, db: Session = Depends(get_db_session)
):
    return DataProductService().update_data_product(id, data_product, db)


@router.post(
    "/{id}/data_output",
    responses={
        200: {
            "description": "DataOutput successfully created",
            "content": {
                "application/json": {
                    "example": {"id": "random id of the new data_output"}
                }
            },
        },
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                AuthorizationAction.DATA_PRODUCT__CREATE_DATA_OUTPUT,
                DataProductResolver,
            )
        )
    ],
)
def create_data_output(
    id: UUID,
    data_output: DataOutputCreateRequest,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> dict[str, UUID]:
    return DataOutputService().create_data_output(
        id, data_output, db, authenticated_user
    )


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
    dependencies=[Depends(OnlyWithProductAccessID())],
)
def update_data_product_about(
    id: UUID,
    data_product: DataProductAboutUpdate,
    db: Session = Depends(get_db_session),
):
    return DataProductService().update_data_product_about(id, data_product, db)


@router.put(
    "/{id}/status",
    responses={
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        }
    },
    dependencies=[Depends(OnlyWithProductAccessID())],
)
def update_data_product_status(
    id: UUID,
    data_product: DataProductStatusUpdate,
    db: Session = Depends(get_db_session),
):
    return DataProductService().update_data_product_status(id, data_product, db)


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
    dependencies=[Depends(OnlyWithProductAccessID([DataProductUserRole.OWNER]))],
)
def link_dataset_to_data_product(
    id: UUID,
    dataset_id: UUID,
    background_tasks: BackgroundTasks,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
):
    return DataProductService().link_dataset_to_data_product(
        id, dataset_id, authenticated_user, db, background_tasks
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
    dependencies=[Depends(OnlyWithProductAccessID([DataProductUserRole.OWNER]))],
)
def unlink_dataset_from_data_product(
    id: UUID,
    dataset_id: UUID,
    db: Session = Depends(get_db_session),
):
    return DataProductService().unlink_dataset_from_data_product(id, dataset_id, db)


@router.get("/{id}/role", dependencies=[Depends(OnlyWithProductAccessID())])
def get_role(id: UUID, environment: str, db: Session = Depends(get_db_session)) -> str:
    return DataProductService().get_data_product_role_arn(id, environment, db)


@router.get(
    "/{id}/signin_url",
    dependencies=[Depends(OnlyWithProductAccessID())],
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
    "/{id}/conveyor_ide_url",
    dependencies=[Depends(OnlyWithProductAccessID())],
)
def get_conveyor_ide_url(id: UUID, db: Session = Depends(get_db_session)) -> str:
    return DataProductService().get_conveyor_ide_url(id, db)


@router.get(
    "/{id}/databricks_workspace_url",
    dependencies=[Depends(OnlyWithProductAccessID())],
)
def get_databricks_workspace_url(
    id: UUID,
    environment: str,
    db: Session = Depends(get_db_session),
) -> str:
    return DataProductService().get_databricks_workspace_url(id, environment, db)


@router.get("/{id}/data_outputs")
def get_data_outputs(
    id: UUID, db: Session = Depends(get_db_session)
) -> list[DataOutputGet]:
    return DataProductService().get_data_outputs(id, db)


@router.get("/{id}/graph")
def get_graph_data(
    id: UUID, db: Session = Depends(get_db_session), level: int = 3
) -> Graph:
    return DataProductService().get_graph_data(id, level, db)


@router.post(
    "/{id}/settings/{setting_id}",
    dependencies=[Depends(OnlyWithProductAccessID([DataProductUserRole.OWNER]))],
)
def set_value_for_data_product(
    id: UUID,
    setting_id: UUID,
    value: str,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
):
    return DataProductSettingService().set_value_for_product(
        setting_id, id, value, authenticated_user, db
    )
