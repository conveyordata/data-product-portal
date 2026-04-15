from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.configuration.data_product_lifecycles.schema_request import (
    DataProductLifeCycleCreate,
    DataProductLifeCycleUpdate,
)
from app.configuration.data_product_lifecycles.schema_response import (
    CreateDataProductLifeCycleResponse,
    DataProductLifeCyclesGet,
    UpdateDataProductLifeCycleResponse,
)
from app.configuration.data_product_lifecycles.service import (
    DataProductLifeCycleService,
)
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.database import get_db_session

router = APIRouter(
    tags=["Configuration - Data Product lifecycles"],
    prefix="/v2/configuration/data_product_lifecycle",
)


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
) -> CreateDataProductLifeCycleResponse:
    return DataProductLifeCycleService(db).create_data_product_lifecycle(
        data_product_lifecycle
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
) -> UpdateDataProductLifeCycleResponse:
    return DataProductLifeCycleService(db).update_data_product_lifecycle(
        id, data_product_lifecycle
    )


@router.delete(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def remove_data_product_lifecycle(
    id: UUID,
    db: Session = Depends(get_db_session),
) -> None:
    return DataProductLifeCycleService(db).delete_data_product_lifecycle(id)


@router.get("")
def get_data_products_lifecycles(
    db: Session = Depends(get_db_session),
) -> DataProductLifeCyclesGet:
    return DataProductLifeCyclesGet(
        data_product_life_cycles=DataProductLifeCycleService(
            db
        ).get_data_product_lifecycles()
    )
