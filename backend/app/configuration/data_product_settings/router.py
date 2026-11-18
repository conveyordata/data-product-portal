from uuid import UUID

from fastapi import APIRouter, Depends

from app.configuration.data_product_settings.schema_request import (
    DataProductSettingCreate,
    DataProductSettingUpdate,
)
from app.configuration.data_product_settings.schema_response import (
    CreateDataProductSettingResponse,
    DataProductSettingsGet,
    UpdateDataProductSettingResponse,
)
from app.configuration.data_product_settings.service import DataProductSettingService
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.deps import DbSession

router = APIRouter(
    tags=["Configuration - Data Product settings"],
    prefix="/v2/configuration/data_product_settings",
)


@router.post(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def create_data_product_setting(
    setting: DataProductSettingCreate,
    db: DbSession,
) -> CreateDataProductSettingResponse:
    return DataProductSettingService(db).create_data_product_setting(setting)


@router.put(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def update_data_product_setting(
    id: UUID,
    setting: DataProductSettingUpdate,
    db: DbSession,
) -> UpdateDataProductSettingResponse:
    return DataProductSettingService(db).update_data_product_setting(id, setting)


@router.delete(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def remove_data_product_setting(
    id: UUID,
    db: DbSession,
) -> None:
    return DataProductSettingService(db).delete_data_product_setting(id)


@router.get("")
def get_data_products_settings(
    db: DbSession,
) -> DataProductSettingsGet:
    return DataProductSettingsGet(
        data_product_settings=DataProductSettingService(db).get_data_product_settings()
    )
