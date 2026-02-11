from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.configuration.data_product_types.schema_request import (
    DataProductTypeCreate,
    DataProductTypeUpdate,
)
from app.configuration.data_product_types.schema_response import (
    CreateDataProductTypeResponse,
    DataProductTypeGet,
    DataProductTypesGet,
    DataProductTypesGetItem,
    UpdateDataProductTypeResponse,
)
from app.configuration.data_product_types.service import DataProductTypeService
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.database import get_db_session

router = APIRouter()


@router.get("/{id}")
def get_data_product_type(
    id: UUID, db: Session = Depends(get_db_session)
) -> DataProductTypeGet:
    return DataProductTypeService(db).get_data_product_type(id)


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
def create_data_product_type(
    data_product_type: DataProductTypeCreate, db: Session = Depends(get_db_session)
) -> CreateDataProductTypeResponse:
    return DataProductTypeService(db).create_data_product_type(data_product_type)


@router.put(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def update_data_product_type(
    id: UUID,
    data_product_type: DataProductTypeUpdate,
    db: Session = Depends(get_db_session),
) -> UpdateDataProductTypeResponse:
    return DataProductTypeService(db).update_data_product_type(id, data_product_type)


@router.delete(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def remove_data_product_type(id: UUID, db: Session = Depends(get_db_session)) -> None:
    return DataProductTypeService(db).remove_data_product_type(id)


@router.put(
    "/migrate/{from_id}/{to_id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def migrate_data_product_type(
    from_id: UUID, to_id: UUID, db: Session = Depends(get_db_session)
) -> None:
    return DataProductTypeService(db).migrate_data_product_type(from_id, to_id)


_router = router
router = APIRouter(tags=["Configuration - Data Product types"])
router.include_router(_router, prefix="/data_product_types", deprecated=True)
router.include_router(_router, prefix="/v2/configuration/data_product_types")


@router.get("/data_product_types", deprecated=True)
def get_data_products_types_old(
    db: Session = Depends(get_db_session),
) -> Sequence[DataProductTypesGetItem]:
    return get_data_products_types(db).data_product_types


@router.get("/v2/configuration/data_product_types")
def get_data_products_types(
    db: Session = Depends(get_db_session),
) -> DataProductTypesGet:
    return DataProductTypesGet(
        data_product_types=DataProductTypeService(db).get_data_product_types()
    )
