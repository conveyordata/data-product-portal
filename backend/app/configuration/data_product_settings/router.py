from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.configuration.data_product_settings.enums import DataProductSettingScope
from app.configuration.data_product_settings.schema_request import (
    DataProductSettingCreate,
    DataProductSettingUpdate,
)
from app.configuration.data_product_settings.schema_response import (
    CreateDataProductSettingResponse,
    DataProductSettingsGet,
    DataProductSettingsGetItem,
    UpdateDataProductSettingResponse,
)
from app.configuration.data_product_settings.service import DataProductSettingService
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.core.namespace.validation import (
    NamespaceLengthLimits,
    NamespaceSuggestion,
    NamespaceValidation,
)
from app.database.database import get_db_session

router = APIRouter()


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
    db: Session = Depends(get_db_session),
) -> CreateDataProductSettingResponse:
    return DataProductSettingService(db).create_data_product_setting(setting)


@router.get("/namespace_suggestion", deprecated=True)
def get_data_product_settings_namespace_suggestion(name: str) -> NamespaceSuggestion:
    return DataProductSettingService.data_product_settings_namespace_suggestion(name)


@router.get("/validate_namespace", deprecated=True)
def validate_data_product_settings_namespace(
    namespace: str,
    scope: DataProductSettingScope,
    db: Session = Depends(get_db_session),
) -> NamespaceValidation:
    return DataProductSettingService(db).validate_data_product_settings_namespace(
        namespace, scope
    )


@router.get("/namespace_length_limits", deprecated=True)
def get_data_product_settings_namespace_length_limits() -> NamespaceLengthLimits:
    return DataProductSettingService.data_product_settings_namespace_length_limits()


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
    db: Session = Depends(get_db_session),
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
def delete_data_product_setting(
    id: UUID,
    db: Session = Depends(get_db_session),
) -> None:
    return DataProductSettingService(db).delete_data_product_setting(id)


_router = router
router = APIRouter(tags=["Configuration - Data product settings"])
router.include_router(_router, prefix="/data_product_settings", deprecated=True)
router.include_router(_router, prefix="/v2/configuration/data_product_settings")


@router.get("/data_product_settings", deprecated=True)
def get_data_products_settings_old(
    db: Session = Depends(get_db_session),
) -> Sequence[DataProductSettingsGetItem]:
    return get_data_products_settings(db).data_product_settings


@router.get("/v2/configuration/data_product_settings")
def get_data_products_settings(
    db: Session = Depends(get_db_session),
) -> DataProductSettingsGet:
    return DataProductSettingsGet(
        data_product_settings=DataProductSettingService(db).get_data_product_settings()
    )
