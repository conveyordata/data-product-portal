from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization, DataProductResolver
from app.data_product_settings.schema import (
    DataProductSetting,
    DataProductSettingCreate,
    DataProductSettingUpdate,
)
from app.data_product_settings.service import DataProductSettingService
from app.database.database import get_db_session
from app.dependencies import only_for_admin

router = APIRouter(prefix="/data_product_settings", tags=["data_product_settings"])


@router.get("")
def get_data_products_settings(
    db: Session = Depends(get_db_session),
) -> list[DataProductSetting]:
    return DataProductSettingService().get_data_product_settings(db)


@router.post(
    "",
    dependencies=[
        Depends(only_for_admin),
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_CONFIGURATION, DataProductResolver
            )
        ),
    ],
)
def create_data_product_setting(
    setting: DataProductSettingCreate,
    db: Session = Depends(get_db_session),
):
    return DataProductSettingService().create_data_product_setting(setting, db)


@router.put(
    "/{id}",
    dependencies=[
        Depends(only_for_admin),
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_CONFIGURATION, DataProductResolver
            )
        ),
    ],
)
def update_data_product_setting(
    id: UUID,
    setting: DataProductSettingUpdate,
    db: Session = Depends(get_db_session),
):
    return DataProductSettingService().update_data_product_setting(id, setting, db)


@router.delete(
    "/{id}",
    dependencies=[
        Depends(only_for_admin),
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_CONFIGURATION, DataProductResolver
            )
        ),
    ],
)
def delete_data_product_setting(
    id: UUID,
    db: Session = Depends(get_db_session),
):
    return DataProductSettingService().delete_data_product_setting(id, db)
