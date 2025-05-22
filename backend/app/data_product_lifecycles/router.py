from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.data_product_lifecycles.schema_request import (
    DataProductLifeCycleCreate,
    DataProductLifeCycleUpdate,
)
from app.data_product_lifecycles.schema_response import DataProductLifeCyclesGet
from app.data_product_lifecycles.service import DataProductLifeCycleService
from app.database.database import get_db_session

router = APIRouter(prefix="/data_product_lifecycles", tags=["data_product_lifecycles"])


@router.get("")
def get_data_products_lifecycles(
    db: Session = Depends(get_db_session),
) -> list[DataProductLifeCyclesGet]:
    return DataProductLifeCycleService().get_data_product_lifecycles(db)


@router.post(
    "",
    responses={
        200: {
            "description": "Data Product successfully created",
            "content": {
                "application/json": {
                    "example": {"id": "random id of the new data product"}
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
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def create_data_product_lifecycle(
    data_product_lifecycle: DataProductLifeCycleCreate,
    db: Session = Depends(get_db_session),
) -> dict[str, UUID]:
    return DataProductLifeCycleService().create_data_product_lifecycle(
        data_product_lifecycle, db
    )


@router.put(
    "/{id}",
    responses={
        200: {
            "description": "Data Product lifecycle updated",
            "content": {
                "application/json": {
                    "example": {"id": "random id of the updated data product lifecycle"}
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
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def update_data_product_lifecycle(
    id: UUID,
    data_product_lifecycle: DataProductLifeCycleUpdate,
    db: Session = Depends(get_db_session),
) -> dict[str, UUID]:
    return DataProductLifeCycleService().update_data_product_lifecycle(
        id, data_product_lifecycle, db
    )


@router.delete(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def delete_data_product_lifecycle(
    id: UUID,
    db: Session = Depends(get_db_session),
):
    return DataProductLifeCycleService().delete_data_product_lifecycle(id, db)
